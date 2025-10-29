"""Example building a large heavy-hex circuit with 3 repeated layers of random gates,
generating the tensor network representation using ITN and then sampling bitstrings"""

import random
from datetime import datetime

import numpy as np
from juliacall import Main as jl
from qiskit import transpile, QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_circuit_layout

from itensornetworks_qiskit.graph import extract_cx_gates, map_onto_2d_grid
from itensornetworks_qiskit.sample import itn_samples_to_counts_dict
from itensornetworks_qiskit.utils import qiskit_circ_to_itn_circ_2d

jl.seval("using ITensorNetworksQiskit")

# Any Julia functions from outside our package should be added here
jl.seval("using ITensorNetworks: siteinds, maxlinkdim")

cmap = CouplingMap().from_heavy_hex(5)
n_qubits = cmap.size()
print(f"Created heavy-hex graph with {cmap.size()} qubits")
backend = GenericBackendV2(n_qubits, coupling_map=cmap)

graph = backend.coupling_map.get_edges()
# Remove duplicates with opposite direction
edges = [list(s) for s in set([frozenset(item) for item in graph])]

# Generate a map between the qubit indices and a 2d coordinate grid. This can take a very long
# time for large graphs!
qmap = map_onto_2d_grid(edges)

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
plot_circuit_layout(qc, backend, qubit_coordinates=[qmap[i] for i in range(n_qubits)]).show()

cmap = backend.coupling_map

# Make the 2d coordinate mapping 1-indexed for Julia
qmap = {k + 1: tuple(q + 1 for q in v) for k, v in qmap.items()}

# convert circuit to required ITN format
itn_circ = qiskit_circ_to_itn_circ_2d(qc, qmap=qmap)

# build ITN graph from the Qiskit circuit
cx_gates = extract_cx_gates(itn_circ)
g = jl.build_graph_from_gates(jl.seval(cx_gates))
s = jl.siteinds("S=1/2", g)

# set a desired maximum bond dimension
chi = 50
start_time = datetime.now()

# run simulation
# extract output MPS and belief propagation cache (bpc)
psi, bpc, errors = jl.tn_from_circuit(itn_circ, chi, s)
print("Maximum bond dimension", jl.maxlinkdim(psi))
print("Estimated final state fidelity:", np.prod(1 - np.array(errors)))

print(f"Sampling from circuit")
num_shots = 10
itn_shots = jl.sample_psi(psi, num_shots, 5, 5)

t = datetime.now() - start_time
print(f"Simulation and sampling completed in {t}")

shots = itn_samples_to_counts_dict(itn_shots, qmap)
print(f"Shot counts of the circuit: {shots}")
