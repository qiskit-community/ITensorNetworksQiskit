const TN = TensorNetworkQuantumSimulator

#TODO: Rewrite the documentation
#TODO: Remove no-longer used functions

"""
    tn_from_circuit(gates, chi, s, nlayers, bp_update_freq)

Returns an ITensorNetwork corresponding to the action of the gates on the |00..0> state. See the
/examples/ directory for examples of usage.

Belief propagation uses the default convergence settings defined in
https://github.com/JoeyT1994/TensorNetworkQuantumSimulator/blob/main/src/Backend/beliefpropagation.jl.
Furthermore, the belief propagation cache is updated every time an overlapping gate is encountered
(i.e., every time the two-qubit circuit depth increases), the default behaviour in
TensorNetworkQuantumSimulator.

"""
function tn_from_circuit(circuit_data::Any,qubit_map::Any,connectivity_qiskit::Any,chi::Any,cutoff::Any)
  circuit_data, qubit_map, connectivity_qiskit = py_translate_circuit(circuit_data, qubit_map, connectivity_qiskit)
  list_gates=translate_circuit(circuit_data,qubit_map)
  g=get_graph(connectivity_qiskit,qubit_map)

  ψ = tensornetworkstate(ComplexF32, v -> "↑", g, "S=1/2")
  ψ_bpc = BeliefPropagationCache(ψ)
  χ = 5
  apply_kwargs = (; cutoff = cutoff, maxdim = chi, normalize_tensors = true)
  ψ_bpc, errs = apply_gates(list_gates, ψ_bpc; apply_kwargs)
  return ψ_bpc, errs
end
