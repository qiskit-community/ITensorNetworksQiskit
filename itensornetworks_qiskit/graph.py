import re

import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
from qiskit import QuantumCircuit


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


def map_onto_2d_grid(edges: list[list[int]], num_x: int = 10, num_y: int = 10):
    """
    Lay out a planar graph on an integer 2D grid.
    :param edges: Undirected edge list, e.g. [[0, 1], [1, 2], … ].
    :param num_x: Number of rows in the grid
    :param num_y: Number of columns in the grid
    """
    g = nx.Graph(edges)
    square_g = nx.grid_2d_graph(num_x, num_y)
    matcher = GraphMatcher(square_g, g)
    coords_to_qubits = next(matcher.subgraph_isomorphisms_iter())
    qubits_to_coords = {v: k for k, v in coords_to_qubits.items()}

    return qubits_to_coords
