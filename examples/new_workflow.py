import numpy as np
from qiskit.primitives import StatevectorSampler
from juliacall import Main as jl
from qiskit.circuit.library import real_amplitudes
from qiskit.quantum_info import SparsePauliOp, Statevector

from itensornetworks_qiskit.convert import observable_description, circuit_description
from itensornetworks_qiskit.graph import graph_from_edges, graph_to_grid

jl.seval("using ITensorNetworksQiskit")
jl.seval("using TensorNetworkQuantumSimulator")

qc = real_amplitudes(10, entanglement="circular")
qc.assign_parameters(np.arange(qc.num_parameters), inplace=True)

circuit, qiskit_connectivity = circuit_description(qc)
graph = graph_from_edges(qiskit_connectivity)
qubit_map = graph_to_grid(graph, 10)
# print(qubit_map)

bpc, error = jl.tn_from_circuit(circuit, qubit_map, qiskit_connectivity, 5, 1e-12)
print("Sampling...")
jl_samples = jl.sample_psi(bpc, 200, 5, 5)
jl_samples_translated = jl.translate_samples(jl_samples, qubit_map)
samples = jl.pydict(jl_samples_translated)
print(samples)


hamiltonian = SparsePauliOp.from_sparse_list(
    [("XX", [i, j], 1.0) for i, j in qiskit_connectivity], qc.num_qubits
)
obs_jl = jl.translate_observable(observable_description(hamiltonian), qubit_map)
exp_val = jl.sum(jl.expect(bpc, obs_jl))
print(exp_val)
