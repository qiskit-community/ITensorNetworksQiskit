"""Example building a large heavy-hex circuit with 3 repeated layers of random gates,
generating the tensor network representation using ITN and then sampling bitstrings"""

import random
from datetime import datetime

import numpy as np
from juliacall import Main as jl
from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_circuit_layout
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

from itensornetworks_qiskit.convert import circuit_description
from itensornetworks_qiskit.graph import (
    graph_from_edges,
    graph_to_grid,
)
from itensornetworks_qiskit.ibm_device_map import ibm_qubit_layout

jl.seval("using ITensorNetworksQiskit")


cmap = CouplingMap().from_heavy_hex(3)
n_qubits = cmap.size()
print(f"Created heavy-hex graph with {cmap.size()} qubits")
backend = GenericBackendV2(n_qubits, coupling_map=cmap)

graph = backend.coupling_map.get_edges()
# Remove duplicates with opposite direction
edges = tuple([tuple(s) for s in set([frozenset(item) for item in graph])])


qc = QuantumCircuit(backend.num_qubits)
num_layers = 5
for i in range(num_layers):
    for edge in graph:
        qc.h(edge[0])
        qc.h(edge[1])
        qc.cx(edge[0], edge[1])
        qc.ry(random.random() * np.pi, edge[0])
        qc.ry(random.random() * np.pi, edge[1])

qmap = graph_to_grid(graph_from_edges(edges))
# TODO: I can not visualize this but it might be a problem of my system
# plot_circuit_layout(
#     qc, backend, qubit_coordinates=[qmap[i][1] for i in range(n_qubits)]
# ).show()

circuit, qiskit_connectivity = circuit_description(qc)
graph = graph_from_edges(qiskit_connectivity)

# set a desired maximum bond dimension
chi = 5
cutoff = 1e-12
bpc, errors = jl.tn_from_circuit(circuit, qmap, qiskit_connectivity, chi, cutoff)
print("Sampling from circuit")
samples = jl.sample_psi(bpc, 50, chi, chi)
samples_qiskit = []
for sample in samples:
    samples_qiskit.append(([jl.get(sample, coord, None) for _, coord in qmap]))

start_time = datetime.now()

# TODO: I don't know what the next method has been renamed to
# print("Maximum bond dimension", jl.maxlinkdim(bpc))
print("Estimated final state fidelity:", np.prod(1 - np.array(errors)))

print("Sampling from circuit")
num_shots = 10
itn_shots = jl.sample_psi(bpc, num_shots, 5, 5)

t = datetime.now() - start_time
print(f"Simulation and sampling completed in {t}")

shots = jl.pydict(jl.translate_samples(itn_shots, qmap))
print(f"Shot counts of the circuit: {shots}")
