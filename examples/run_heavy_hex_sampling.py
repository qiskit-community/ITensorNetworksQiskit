"""Example building a large heavy-hex circuit using real device topology, applying 3 repeated
layers of random gates, generating the tensor network representation using ITN and then sampling
bitstrings"""

import random

import numpy as np
from datetime import datetime
from juliacall import Main as jl
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_circuit_layout
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

from itensornetworks_qiskit.convert import circuit_description
from itensornetworks_qiskit.graph import graph_from_edges, graph_to_grid
from itensornetworks_qiskit.ibm_device_map import ibm_qubit_layout

jl.seval("using ITensorNetworksQiskit")

backend = FakeSherbrooke()
n_qubits = backend.num_qubits
cmap = backend.coupling_map
print(f"Created heavy-hex graph from {backend.name} with {cmap.size()} qubits")

graph = backend.coupling_map.get_edges()

# Remove duplicates with opposite direction
edges = [list(s) for s in set([frozenset(item) for item in graph])]

qc = QuantumCircuit(backend.num_qubits)
for _ in range(3):
    for edge in edges[:]:
        qc.h(edge[0])
        qc.h(edge[1])
        qc.cx(edge[0], edge[1])
        qc.ry(random.random() * np.pi, edge[0])
        qc.ry(random.random() * np.pi, edge[1])

qc = transpile(qc, backend, basis_gates=["cx", "h", "rx", "ry"])

circuit, qmap = circuit_description(qc)
graph = graph_from_edges(qmap)
plot_circuit_layout(
    qc, backend, qubit_coordinates=[qmap[i][1] for i in range(n_qubits)]
).show()
# Set tensor network truncation parameters
chi = 5
cutoff = 1e-12

start_time = datetime.now()
bpc, errors = jl.tn_from_circuit(circuit, qmap, qmap, chi, cutoff)
print("Estimated final state fidelity:", np.prod(1 - np.array(errors)))

print("Sampling from circuit")
num_shots = 10
projected_mps_bond_dimension = 5
norm_mps_bond_dimension = 5
samples = jl.sample_psi(
    bpc, num_shots, projected_mps_bond_dimension, norm_mps_bond_dimension
)

t = datetime.now() - start_time
print(f"Simulation and sampling completed in {t}")

shots = jl.pydict(jl.translate_samples(samples, qmap))
print(f"Shot counts of the circuit: {shots}")
