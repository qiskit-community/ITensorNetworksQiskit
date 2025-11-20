using TensorNetworkQuantumSimulator
using TensorNetworkQuantumSimulator: expect

using ITensors: ITensors
using ITensors: Index, ITensor, hasqns, noncommonind, combinedind, combiner, replaceinds, sim, onehot, delta, plev, dense, unioninds, uniqueinds, commonind, commoninds, replaceind, datatype, inds, dag, noprime, factorize_svd, prime, hascommoninds, itensor, map_diag!, @Algorithm_str, scalar, @OpName_str, @SiteType_str, denseblocks, tags
using ITensorMPS
using ITensorNetworks: ITensorNetwork

using Dictionaries: Dictionary, set!

using Graphs
using Graphs: simplecycles_limited_length, has_edge, SimpleGraph, center, steiner_tree, is_tree, vertices, nv

using NamedGraphs
using NamedGraphs:
    AbstractNamedGraph,
    AbstractGraph,
    AbstractEdge,
    position_graph,
    rename_vertices,
    edges,
    vertextype,
    add_vertex!,
    neighbors,
    edgeinduced_subgraphs_no_leaves,
    unique_cyclesubgraphs_limited_length
using NamedGraphs.GraphsExtensions:
    src,
    dst,
    subgraph,
    is_connected,
    degree,
    add_edge,
    a_star,
    add_edge!,
    edgetype,
    leaf_vertices,
    post_order_dfs_edges,
    decorate_graph_edges,
    add_vertex!,
    add_vertex,
    rem_edge,
    rem_vertex,
    add_edges,
    rem_vertices,
    rem_vertex!

using NamedGraphs.NamedGraphGenerators: named_grid, named_hexagonal_lattice_graph, named_comb_tree, named_path_graph

using TensorOperations