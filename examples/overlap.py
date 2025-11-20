from juliacall import Main as jl
from itensornetworks_qiskit.marc import parse_circuit, graph_from_edges, graph_to_grid
from qiskit.circuit.library import real_amplitudes
import numpy as np


jl.seval("using ITensorNetworksQiskit")


#### Main

qc = real_amplitudes(4, entanglement="circular")
# qc.pauli("XXXY", [0, 1, 2, 3])
qcA = qc.assign_parameters(np.arange(qc.num_parameters))
qcB = qc.assign_parameters(-np.arange(qc.num_parameters))


def get_tn(qc):
    circuit, qiskit_connectivity = parse_circuit(qc)
    circuit = tuple(((a, b, tuple(d * 1.0j for d in c))) for a, b, c in circuit)
    graph = graph_from_edges(qiskit_connectivity)
    qubit_map = graph_to_grid(graph, 10)
    bpc, error = jl.tn_from_qiskit_circuit(circuit, qubit_map, qiskit_connectivity)
    return bpc


tnA = get_tn(qcA)
tnB = get_tn(qcB)
