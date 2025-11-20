"""Example building a large heavy-hex circuit with 5 repeated layers of random gates,
generating the tensor network representation using ITN and then computing observables"""

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
jl.seval("using TensorNetworkQuantumSimulator: network")
jl.seval("using ITensorNetworks: siteinds")

backend = FakeSherbrooke()
n_qubits = backend.num_qubits
cmap = backend.coupling_map
print(f"Created heavy-hex graph from {backend.name} with {cmap.size()} qubits")

graph = backend.coupling_map.get_edges()

# Remove duplicates with opposite direction
edges = [list(s) for s in set([frozenset(item) for item in graph])]

qc = QuantumCircuit(backend.num_qubits)
num_layers = 5
for i in range(num_layers):
    for edge in graph:
        qc.h(edge[0])
        qc.h(edge[1])
        qc.cx(edge[0], edge[1])
        qc.ry(random.random() * np.pi, edge[0])
        qc.ry(random.random() * np.pi, edge[1])

qc = transpile(qc, basis_gates=["rx", "ry", "rz", "cx"], backend=backend)
qmap = graph_to_grid(graph_from_edges(edges))
# plot_circuit_layout(qc, backend, qubit_coordinates=[qmap[i][1] for i in range(n_qubits)]).show()

circuit, qiskit_connectivity = circuit_description(qc)
graph = graph_from_edges(qiskit_connectivity)

# Set tensor network truncation parameters
chi = 10
cutoff = 1e-12

start_time = datetime.now()
psi_bpc, errors = jl.tn_from_circuit(circuit, qmap, qiskit_connectivity, chi, cutoff)
print("Estimated final state fidelity:", np.prod(1 - np.array(errors)))

t = datetime.now() - start_time
print(t)

print("***** ITN results *****")
# TODO Figure out how to use get_graph. Once we do we can caller inner() and it should work
g = jl.get_graph(qiskit_connectivity, qmap)
s = jl.siteinds("S=1/2", g)
itn_overlap = jl.overlap_with_zero(psi_bpc, s)
print(f"Overlap with zero state: {itn_overlap}")

# Compute Z expectation values of qubits 0 and 1. We need to provide the 2d graph coordinate
qmap_dict = {k: v for k, v in qmap}
sites = [qmap_dict[qubit] for qubit in [1, 2]]
z_eval = jl.pauli_expectation("Z", psi_bpc, sites)

# TODO get this working or drop it, it's not in TNQS and is based on code we had that took an ITensorNetwork as input, Joey can help maybe
psi = jl.network(psi_bpc)
rdm = jl.rdm(psi, sites)

print(f"σz expectation value of sites 1 and 2: {z_eval}")
print(f"2-qubit RDM of sites of first edge: {rdm}")
print("\n")
