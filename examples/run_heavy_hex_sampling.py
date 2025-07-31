"""Example building a large heavy-hex circuit with 3 repeated layers of random gates,
generating the tensor network representation using ITN and then sampling bitstrings"""

import random
from datetime import datetime

import numpy as np
from juliacall import Main as jl
from qiskit import transpile, QuantumCircuit
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

from itensornetworks_qiskit.graph import extract_cx_gates
from itensornetworks_qiskit.ibm_device_map import ibm_qubit_layout
from itensornetworks_qiskit.sample import itn_samples_to_counts_dict
from itensornetworks_qiskit.utils import qiskit_circ_to_itn_circ_2d

jl.seval("using ITensorNetworksQiskit")

# Any Julia functions from outside our package should be added here
jl.seval("using ITensorNetworks: siteinds")

# Note here we use a real device graph, which is subtly different from CouplingMap().from_heavy_hex
# used in other examples. Any connectivity can be used if a map can be provided between qubit
# indices and a 2D coordinate grid.
backend = FakeSherbrooke()
n_qubits = backend.num_qubits
cmap = backend.coupling_map
print(f"Created heavy-hex graph with {cmap.size()} qubits")

graph = backend.coupling_map.get_edges()

# Remove duplicates with opposite direction
graph = [list(s) for s in set([frozenset(item) for item in graph])]

qc = QuantumCircuit(backend.num_qubits)
for _ in range(3):
    for edge in graph:
        qc.h(edge[0])
        qc.h(edge[1])
        qc.cx(edge[0], edge[1])
        qc.ry(random.random() * np.pi, edge[0])
        qc.ry(random.random() * np.pi, edge[1])

qc = transpile(qc, basis_gates=["rx", "ry", "rz", "cx"], backend=backend)

# Define a 1-indexed map from qubit indices to 2d integer coordinate grid (needed for sampling)
two_d_layout = ibm_qubit_layout[n_qubits]
qmap = {i + 1: tuple(q + 1 for q in two_d_layout[i]) for i in range(n_qubits)}

# convert circuit to required ITN format
itn_circ = qiskit_circ_to_itn_circ_2d(qc, qmap=qmap)

# build ITN graph from the Qiskit circuit
cx_gates = extract_cx_gates(itn_circ)
g = jl.build_graph_from_gates(jl.seval(cx_gates))
s = jl.siteinds("S=1/2", g)

# set a desired maximum bond dimension
chi = 50
start_time = datetime.now()

# run simulation: Note obtaining the state and sampling takes ~2 minutes to run

# extract output MPS and belief propagation cache (bpc)
psi, bpc, errors = jl.tn_from_circuit(itn_circ, chi, s)
print("Estimated final state fidelity:", np.prod(1 - np.array(errors)))

print(f"Sampling from circuit")
num_shots = 10
itn_shots = jl.sample_psi(psi, num_shots, 5, 5)

t = datetime.now() - start_time
print(f"Simulation and sampling completed in {t}")

shots = itn_samples_to_counts_dict(itn_shots, qmap)
print(f"Shot counts of the circuit: {shots}")
