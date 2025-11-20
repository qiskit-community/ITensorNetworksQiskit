using Graphs
using NamedGraphs
using TensorNetworkQuantumSimulator
using NamedGraphs: NamedGraphs, neighbors
using ITensors: ITensor, ITensors

function get_graph(connectivity_qiskit::Any,qubit_map::Any)
  circuit_data,qubit_map,connectivity_qiskit=py_translate([],qubit_map,connectivity_qiskit)
  return get_graph(connectivity_qiskit,qubit_map)
end
function get_graph(connectivity_qiskit::Vector{Tuple{Int,Int}},qubit_map::Dict{Int,Tuple{Int,Int}})
  nodes_qiskit=Set([q for pair in connectivity_qiskit for q in pair])

  g = NamedGraph{Tuple{Int, Int}}()

  # Add nodes
  for node in nodes_qiskit
    add_vertex!(g, Tuple(qubit_map[node]))
  end

  # Add edges
  for edge in connectivity_qiskit 
    add_edge!(g, Tuple([Tuple(qubit_map[e]) for e in edge]))
    add_edge!(g, Tuple([Tuple(qubit_map[e]) for e in edge]))
  end
  return g
end
