"""Example building a large heavy-hex circuit with 3 repeated layers of random gates,
generating the tensor network representation using ITN and then sampling bitstrings"""

import random

import numpy as np
from datetime import datetime
from juliacall import Main as jl
from qiskit import QuantumCircuit
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

from itensornetworks_qiskit.convert import circuit_description
from itensornetworks_qiskit.graph import graph_from_edges, graph_to_grid
from itensornetworks_qiskit.ibm_device_map import ibm_qubit_layout

jl.seval("using ITensorNetworksQiskit")

# Note here we use a real device graph, which is subtly different from CouplingMap().from_heavy_hex
# used in other examples. Any connectivity can be used if a map can be provided between qubit
# indices and a 2D coordinate grid.
backend = FakeSherbrooke()
n_qubits = backend.num_qubits
cmap = backend.coupling_map
print(f"Created heavy-hex graph with {cmap.size()} qubits")

graph = backend.coupling_map.get_edges()

# Remove duplicates with opposite direction
edges = [list(s) for s in set([frozenset(item) for item in graph])]

qc = QuantumCircuit(backend.num_qubits)
for _ in range(1):
    for edge in edges[:]:
        qc.h(edge[0])
        qc.h(edge[1])
        qc.cx(edge[0], edge[1])
        qc.ry(random.random() * np.pi, edge[0])
        qc.ry(random.random() * np.pi, edge[1])

circuit, qiskit_connectivity = circuit_description(qc)
graph = graph_from_edges(qiskit_connectivity)
two_d_layout = ibm_qubit_layout[qc.num_qubits]
qmap = [(i, two_d_layout[i]) for i in range(qc.num_qubits)]


# set a desired maximum bond dimension
chi = 5
cutoff = 1.0e-12
bpc, errors = jl.tn_from_circuit(circuit, qmap, qiskit_connectivity, chi, cutoff)
print("Sampling from circuit")
samples = jl.sample_psi(bpc, 50, chi, chi)
samples_qiskit = []
for sample in samples:
    samples_qiskit.append(([jl.get(sample, coord, None) for _, coord in qmap]))

start_time = datetime.datetime.now()


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
