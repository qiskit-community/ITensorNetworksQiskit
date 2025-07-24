import io
import re
import sys

import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
from qiskit import QuantumCircuit


def extract_itn_graph(g):
    output_capture = io.StringIO()
    sys.stdout = output_capture
    print(g)
    sys.stdout = sys.__stdout__
    julia_output = output_capture.getvalue()
    output_capture.close()
    edges_str = julia_output.split(" edge(s):")[1].strip()
    edge_pattern = re.compile(r"\((\d+),\) => \((\d+),\)")
    edges = edge_pattern.findall(edges_str)
    edges_tuples = [(int(x) - 1, int(y) - 1) for x, y in edges]
    return edges_tuples


def extract_cx_gates(itn_circ: str):
    pattern = r'("CX", \[.*?\])'
    cx_terms = re.findall(pattern, itn_circ)
    modified_cx_terms = ["(" + term + ")" for term in cx_terms]
    joined_cx_terms = ', '.join(modified_cx_terms)
    return "[" + joined_cx_terms + "]"


def cmap_from_circuit(qc: QuantumCircuit):
    edges = []
    for gate in qc:
        if len(gate.qubits) >= 3:
            raise NotImplemented("Please transpile to only 1 and 2 qubit gates")
        if len(gate.qubits) == 2:
            edges.append([gate.qubits[0]._index, gate.qubits[1]._index])
    unique_edges = [list(s) for s in set([frozenset(item) for item in edges])]
    return unique_edges


def map_onto_2d_grid(edges, num_x=10, num_y=10):
    """
    Lay out a planar graph on an integer 2D grid.

    Parameters
    ----------
    edges : list[list[int]]
        Undirected edge list, e.g. [[0, 1], [1, 2], … ].
    num_x : int
        Number of rows in the grid
    num_y : int
        Number of columns in the grid
    Returns
    -------
    dict[int, tuple[int, int]]
        Mapping {original vertex label → (x_int, y_int)}.
    """
    edges_tuple = tuple(tuple(pair) for pair in edges)
    if mapping_cache.get(edges_tuple) is not None:
        return mapping_cache[edges_tuple]
    g = nx.Graph(edges)
    square_g = nx.grid_2d_graph(num_x, num_y)
    matcher = GraphMatcher(square_g, g)
    coords_to_qubits = next(matcher.subgraph_isomorphisms_iter())
    qubits_to_coords = {v: k for k, v in coords_to_qubits.items()}

    return qubits_to_coords


mapping_cache = {}
mapping_cache[((2, 3), (11, 12), (4, 5), (40, 41), (0, 5), (14, 7), (8, 7), (14, 23), (41, 42), (32, 33), (10, 11), (3, 4), (16, 17), (22, 23), (33, 29), (3, 13), (5, 6), (18, 19), (24, 25), (27, 28), (27, 15), (35, 36), (43, 35), (24, 23), (6, 7), (36, 37), (41, 31), (17, 18), (11, 15), (21, 22), (33, 34), (38, 39), (26, 27), (20, 21), (40, 39), (19, 20), (25, 26), (1, 9), (37, 30), (9, 10), (21, 30), (8, 9), (44, 39), (17, 29), (25, 31), (19, 13), (37, 38), (34, 35))
] = {2: (0, 1), 3: (1, 1), 4: (1, 2), 5: (1, 3), 0: (0, 3), 13: (2, 1), 6: (1, 4), 7: (1, 5), 14: (2, 5), 8: (1, 6), 23: (3, 5), 22: (3, 4), 19: (3, 1), 18: (4, 1), 17: (5, 1), 16: (5, 0), 29: (6, 1), 33: (7, 1), 32: (7, 0), 24: (3, 6), 25: (3, 7), 31: (4, 7), 41: (5, 7), 40: (5, 6), 42: (6, 7), 21: (3, 3), 34: (7, 2), 35: (7, 3), 36: (6, 3), 43: (8, 3), 37: (5, 3), 38: (5, 4), 39: (5, 5), 26: (3, 8), 27: (3, 9), 28: (4, 9), 15: (2, 9), 11: (1, 9), 12: (0, 9), 10: (1, 8), 20: (3, 2), 9: (1, 7), 1: (0, 7), 30: (4, 3), 44: (6, 5)}