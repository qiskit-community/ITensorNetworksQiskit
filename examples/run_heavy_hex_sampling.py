"""Example building a large heavy-hex circuit with 10 repeated layers of random gates,
generating the tensor network representation using ITN and then computing observables"""

import random
from datetime import datetime

import numpy as np
from juliacall import Main as jl
from qiskit import transpile, QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_circuit_layout
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeSherbrooke

from itensornetworks_qiskit.ibm_device_map import ibm_qubit_layout
from itensornetworks_qiskit.utils import (
    qiskit_circ_to_itn_circ_2d, prepare_graph_for_itn,
)

jl.seval("using ITensorNetworksQiskit")

# Any Julia functions from outside our package should be added here
jl.seval("using ITensorNetworks: siteinds")
jl.seval("using TensorNetworkQuantumSimulator: sample, maxlinkdim")

backend = FakeSherbrooke()
n_qubits = backend.num_qubits
cmap = backend.coupling_map
print(f"Created heavy-hex graph with {cmap.size()} qubits")

graph = backend.coupling_map.get_edges()

# Remove duplicates with opposite direction
graph = [list(s) for s in set([frozenset(item) for item in graph])]

qc = QuantumCircuit(backend.num_qubits)
for edge in graph:
    qc.h(edge[0])
    qc.h(edge[1])
    qc.cx(edge[0], edge[1])
    qc.ry(random.random() * np.pi, edge[0])
    qc.ry(random.random() * np.pi, edge[1])

qc = transpile(qc, basis_gates=["rx", "ry", "rz", "cx"], backend=backend)
plot_circuit_layout(qc, backend).show()

# Define a 1-indexed map from qubit indices to 2d integer coordinate grid (needed for sampling)
two_d_layout = ibm_qubit_layout[n_qubits]
qmap = {i+1: tuple(q+1 for q in two_d_layout[i]) for i in range(n_qubits)}

# convert circuit to required ITN format
itn_circ = qiskit_circ_to_itn_circ_2d(qc, qmap=qmap)

# build ITN graph from the Qiskit circuit
graph_string = prepare_graph_for_itn(itn_circ)
g = jl.build_graph_from_gates(jl.seval(graph_string))
s = jl.siteinds("S=1/2", g)

# set a desired maximum bond dimension
chi = 50
start_time = datetime.now()

# If a circuit has a repeated structure, we can define how many layers of it here. The belief
# propagation cache will be updated after every layer
n_layers = 5

# run simulation
# extract output MPS and belief propagation cache (bpc)
psi, bpc = jl.tn_from_circuit(itn_circ, chi, s, n_layers)
t = datetime.now() - start_time
print(t)

print("***** ITN results *****")
itn_overlap = jl.overlap_with_zero(psi, s)
itn_eval = jl.pauli_expectation("Z", psi, [qmap[1], qmap[2]], bpc)
itn_rdm = jl.get_first_edge_rdm_2d(psi, bpc, g)
print(f"Overlap with zero state: {itn_overlap}")
print(f"σz expectation value of sites 1 and 2: {itn_eval}")
print(f"2-qubit RDM of sites of first edge: {itn_rdm}")

print(f"Sampling from circuit")

shots = 100
projected_message_rank = jl.maxlinkdim(psi) * 5
norm_message_rank = jl.maxlinkdim(psi) ^ 2
print(jl.sample(psi, shots, projected_message_rank=projected_message_rank,
                norm_message_rank=norm_message_rank))

print("\n")
