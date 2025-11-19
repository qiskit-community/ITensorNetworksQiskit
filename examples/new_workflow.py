import numpy as np
from juliacall import Main as jl
from qiskit.circuit.library import real_amplitudes
from qiskit.quantum_info import SparsePauliOp

from itensornetworks_qiskit.convert import observable_description, circuit_description
from itensornetworks_qiskit.graph import graph_from_edges, graph_to_grid

jl.seval("using ITensorNetworksQiskit")
jl.seval("using TensorNetworkQuantumSimulator")

qc = real_amplitudes(10, entanglement="circular")
qc.assign_parameters(np.arange(qc.num_parameters), inplace=True)

circuit, qiskit_connectivity = circuit_description(qc)
graph = graph_from_edges(qiskit_connectivity)
qubit_map = graph_to_grid(graph, 10)

bpc, error = jl.tn_from_circuit(circuit, qubit_map, qiskit_connectivity)
print("Sampling...")
samples = jl.sample_psi(bpc, 50, 5, 5)
samples_qiskit = []
for sample in samples:
    samples_qiskit.append(([jl.get(sample, coord, None) for _, coord in qubit_map]))
print(samples_qiskit)

hamiltonian = SparsePauliOp.from_sparse_list(
    [("XX", [i, j], 1.0) for i, j in qiskit_connectivity], qc.num_qubits
)
obs_jl = jl.translate_observable(observable_description(hamiltonian), qubit_map)
exp_val = jl.sum(jl.expect(bpc, obs_jl))
print(exp_val)
