import numpy as np
import json
import rustworkx as rx
from qiskit import QuantumCircuit
from rustworkx.generators import grid_graph


### Functions that will go into the library
def graph_from_edges(edges: list[tuple[int, int]]) -> rx.PyGraph:
    """
    Args:
        edges: List with pairs of qubit indices that are connected.
        The indices do not need to start at 0 and there may be gaps between them.
        Ex: [(2,7),(7,5),(5,1),(5,2)]
    Returns a rustworkx graph that matches the connectivity between edges.
    """
    graph = rx.PyGraph()
    qubits = set(qubit_id for pair in edges for qubit_id in pair)
    node_map = dict()
    for qubit_id in qubits:
        node_map[qubit_id] = graph.add_node(
            qubit_id
        )  # We add the node index as node data for the later mapping.
    for qa, qb in edges:
        graph.add_edge(node_map[qa], node_map[qb], None)
    return graph


def graph_to_grid(
    graph: rx.PyGraph, max_grid_size: int = 20
) -> dict[int, tuple[int, int]]:
    square = grid_graph(
        max_grid_size,
        max_grid_size,
        weights=[(x, y) for x in range(max_grid_size) for y in range(max_grid_size)],
    )
    possible_maps = rx.vf2_mapping(square, graph, subgraph=True, id_order=False)
    try:
        graph_map = next(possible_maps)
    except StopIteration:
        raise ValueError(
            """The current graph can not be mapped to a square lattice.
            Try increasing the size of the grid."""
        )
    qubit_map = tuple((graph[v], square[k]) for k, v in graph_map.items())
    return sorted(qubit_map)


def parse_circuit(
    qc: QuantumCircuit,
) -> tuple[
    list[tuple[str, tuple[int, ...], tuple[float, ...]]], tuple[tuple[int, int]]
]:
    # We start by creating the list of circuit instructions
    # We need to check that the instructions are supported and that the parameters are bound.
    # At the same time we will also keep track of the connectivity in the circuit.
    # Any 2 qubit gate will be added to the connectivity, and to avoid counting duplicates
    # we will take the convention that the pairs are (a,b) with a<b.
    assert len(qc.parameters) == 0, "There are some unbound parameters in the circuit."
    circuit = []
    connectivity = set()
    for inst in qc:
        gate_name = inst.name
        qubit_indices = [q._index for q in inst.qubits]
        parameters = inst.params
        circuit.append((gate_name, tuple(qubit_indices), tuple(parameters)))
        if len(qubit_indices) == 2:
            qubit_indices.sort()
            connectivity.add(tuple(qubit_indices))
        elif len(qubit_indices) > 2 and gate_name != "pauli":
            raise NotImplementedError(
                f"Error with gate:{gate_name}. Gates with more than 3 qubits have not been implemented yet"
            )
    return tuple(circuit), tuple(connectivity)
