from juliacall import Main as jl
from qiskit.quantum_info import SparsePauliOp
from itensornetworks_qiskit.marc import (
    parse_circuit,
    graph_from_edges,
    graph_to_grid,
    translate_observable,
)
from qiskit.circuit.library import real_amplitudes
import numpy as np


jl.seval("using ITensorNetworksQiskit")


#### Main

qc = real_amplitudes(4, entanglement="circular")
# qc.pauli("XXXY", [0, 1, 2, 3])
qc.assign_parameters(np.arange(qc.num_parameters), inplace=True)

circuit, qiskit_connectivity = parse_circuit(qc)
graph = graph_from_edges(qiskit_connectivity)
qubit_map = graph_to_grid(graph, 10)


hamiltonian = SparsePauliOp.from_sparse_list(
    [("XX", [i, j], 1.0) for i, j in qiskit_connectivity]
)
print(hamiltonian.to_sparse_list())

print(translate_observable(hamiltonian))


# bpc, error = jl.tn_from_qiskit_circuit(circuit, qubit_map, qiskit_connectivity)
# print("Sampling...")
# samples = jl.sample_psi(bpc, 50, 5, 5)
# samples_qiskit = []
# for sample in samples:
#     samples_qiskit.append(([jl.get(sample, coord, None) for _, coord in qubit_map]))
# print(samples_qiskit)
