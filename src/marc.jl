# using JSON
using Graphs
using NamedGraphs

using TensorNetworkQuantumSimulator
const TN = TensorNetworkQuantumSimulator

using NamedGraphs: NamedGraphs, neighbors

using ITensors: ITensor, ITensors


###Functions for the library


function tn_from_qiskit_circuit(circuit_data::Any,qubit_map::Any,connectivity_qiskit::Any)
  circuit_data,qubit_map,connectivity_qiskit=py_translate(circuit_data,qubit_map,connectivity_qiskit)
  list_gates=translate_circuit(circuit_data,qubit_map)
  g=get_graph(connectivity_qiskit,qubit_map)
  ψ = tensornetworkstate(ComplexF32, v -> "↑", g, "S=1/2")
  ψ_bpc = BeliefPropagationCache(ψ)
  χ = 8
  apply_kwargs = (; cutoff = 1.0e-12, maxdim = χ, normalize_tensors = true)
  ψ_bpc, errs = apply_gates(list_gates, ψ_bpc ;apply_kwargs)
  return ψ_bpc, errs
end


# with open("test_circuit_description.json", "w") as f:
#     json.dump(circuit_description, f)
# print(circuit_description)
  


function py_translate(circuit_data::Any,qubit_map::Any,connectivity_qiskit::Any)
  circuit_data = Vector{Tuple{String, Vector{Int}, Vector{Any}}}([
    (name, Vector{Int}([index for index in indices]), Vector{Any}([parameter for parameter in parameters])) for (name,indices,parameters) in circuit_data
  ])
  qubit_map=Dict{Int, Tuple{Int,Int}}(k => Tuple(v) for (k, v) in qubit_map)
  connectivity_qiskit=Vector{Tuple{Int,Int}}([coord for coord in connectivity_qiskit])
  return circuit_data,qubit_map,connectivity_qiskit
 end

function translate_circuit(circuit_data::Any,qubit_map::Any)
  circuit_data,qubit_map,connectivity_qiskit=py_translate(circuit_data,qubit_map,[])
  return translate_circuit(circuit_data,qubit_map)
end


function translate_circuit(circuit_data::Vector{Tuple{String, Vector{ Int}, Vector{Any}}}, qubit_map::Dict{Int64, Tuple{Int,Int}})
  qubit_map=Dict{Int, Tuple{Int,Int}}(k => Tuple(v) for (k, v) in qubit_map)
  list_gates=[]
  for (qiskit_name,indices,parameter) in circuit_data
    if qiskit_name in keys(name_mapping)
      push!(list_gates,name_mapping[qiskit_name](indices,parameter,qubit_map))
    end
  end
  return list_gates
end


function convertRp(name_gate::String,indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return (name_gate,[qubit_map[index] for index in indices],Float64(parameter[1]))
end

function convertRy(indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return convertRp("Ry",indices,parameter,qubit_map)
end

function convertRxx(indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return ("Rxx",NamedEdge(Tuple(qubit_map[indices[1]])=>Tuple(qubit_map[indices[2]])),0.1)
end

function convertCNOT(indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return ("CNOT",NamedEdge(Tuple(qubit_map[indices[1]])=>Tuple(qubit_map[indices[2]])))
end

name_mapping=Dict("ry"=>convertRy,"cx"=>convertCNOT)


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
