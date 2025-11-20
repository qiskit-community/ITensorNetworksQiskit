using Graphs
using NamedGraphs
using TensorNetworkQuantumSimulator
using NamedGraphs: NamedGraphs, neighbors
using ITensors: ITensor, ITensors

#Translate circuits
function py_translate_circuit(circuit_data::Any,qubit_map::Any,connectivity_qiskit::Any)
  circuit_data = Vector{Tuple{String, Vector{Int}, Vector{Any}}}([
    (name, Vector{Int}([index for index in indices]), Vector{Any}([parameter for parameter in parameters])) for (name,indices,parameters) in circuit_data
  ])
  qubit_map=Dict{Int, Tuple{Int,Int}}(k => Tuple(v) for (k, v) in qubit_map)
  connectivity_qiskit=Vector{Tuple{Int,Int}}([coord for coord in connectivity_qiskit])
  return circuit_data,qubit_map,connectivity_qiskit
 end
function translate_circuit(circuit_data::Any,qubit_map::Any)
  circuit_data,qubit_map,connectivity_qiskit=py_translate_circuit(circuit_data,qubit_map,[])
  return translate_circuit(circuit_data,qubit_map)
end
function translate_circuit(circuit_data::Vector{Tuple{String, Vector{ Int}, Vector{Any}}}, qubit_map::Dict{Int64, Tuple{Int,Int}})
  list_gates=[]
  for (qiskit_name,indices,parameter) in circuit_data
    if qiskit_name in keys(name_mapping)
      push!(list_gates,name_mapping[qiskit_name](indices,parameter,qubit_map))
    else
        throw(ArgumentError("Unsupported gate encountered: $(qiskit_name)."))
    end

  end
  return list_gates
end

#Pauli Rotations
function convertRp(name_gate::String,indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return (name_gate,[qubit_map[index] for index in indices],Float64(parameter[1]))
end
function convertRx(indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return convertRp("Rx",indices,parameter,qubit_map)
end
function convertRy(indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return convertRp("Ry",indices,parameter,qubit_map)
end
function convertRz(indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return convertRp("Rz",indices,parameter,qubit_map)
end
function convertRxx(indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return ("Rxx",NamedEdge(Tuple(qubit_map[indices[1]])=>Tuple(qubit_map[indices[2]])),0.1)
end
function convertRyy(indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return ("Ryy",NamedEdge(Tuple(qubit_map[indices[1]])=>Tuple(qubit_map[indices[2]])),0.1)
end
function convertRzz(indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return ("Rzz",NamedEdge(Tuple(qubit_map[indices[1]])=>Tuple(qubit_map[indices[2]])),0.1)
end

#Non parameterized gates
function convertCNOT(indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return ("CNOT",NamedEdge(Tuple(qubit_map[indices[1]])=>Tuple(qubit_map[indices[2]])))
end
function convertH(indices::Vector{Int},parameter::Vector{Any},qubit_map::Dict{Int, Tuple{Int,Int}})
  return ("H",[qubit_map[indices[1]]])
end
name_mapping=Dict("rx"=>convertRy,
                  "ry"=>convertRy,
                  "rz"=>convertRz,
                  "rxx"=>convertRxx,
                  "ryy"=>convertRyy,
                  "rzz"=>convertRzz,
                  "cx"=>convertCNOT,
                  "h"=>convertH,
                  )

#Translate observables
function translate_observable(obs::Any, qubit_map::Any)
  qubit_map=Dict{Int, Tuple{Int,Int}}(k => Tuple(v) for (k, v) in qubit_map)
  return Vector{Tuple{String,Vector{Tuple{Int,Int}},Float64}}([(term,[qubit_map[index] for index in indices],coeff) for (term,indices,coeff) in obs])
end

function translate_observable(obs::Vector{Tuple{String,Vector{Int},Float64}}, qubit_map::Dict{Int64, Tuple{Int,Int}})
  return Vector{Tuple{String,Vector{Tuple{Int,Int}},Float64}}([(term,Tuple{Int}(qubit_map[indices]),coeff) for (term,indices,coeff) in obs])
end

#Tranlsate samples
function translate_samples(samples::Any,qubit_map::Any)
  samples_qiskit = Vector{String}([])
  for sample in samples
    tranlated_sample=join([sample[coord]  for (qindex, coord ) in qubit_map]) 
    push!(samples_qiskit,tranlated_sample)
  end
  counter=Dict{String,Int}()
  for s in samples_qiskit
      counter[s] = get!(counter, s, 0) + 1
  end
  return counter
end
