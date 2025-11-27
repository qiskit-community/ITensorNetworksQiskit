import rustworkx as rx
from rustworkx.generators import grid_graph


def graph_from_edges(edges: tuple[tuple[int, int], ...]) -> rx.PyGraph:
    """
    Creates a rustworkx graph from a list of edges.
    Args:
        edges: List with pairs of qubit indices that are connected.
        The indices do not need to start at 0 and there may be gaps between them.
        Ex: [(2,7),(7,5),(5,1),(5,2)]
    Returns:
    A rustworkx graph that matches the connectivity between edges.
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
) -> list[tuple[int, tuple[int, int]]]:
    """
    Maps an arbitrary rustworkx graph to a grid. If no mapping exists
    it will raise a ValueError.
    Args:
        graph: An arbitrary rustworkx graph to be mapped to a grid.
        max_grid_size: Number of nodes on each side of the grid lattice.
    Retruns:
    A list with tuples (qubit_index,grid_coordinates) to be
    used for mapping qiskit circuit to TensorNetworkQuantumSimulator.
    """
    # We initialize a square grid. Note that we give as weights
    # julia indices that start at 1.
    square = grid_graph(
        max_grid_size,
        max_grid_size,
        weights=[
            (x + 1, y + 1) for x in range(max_grid_size) for y in range(max_grid_size)
        ],
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
