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

from itensornetworks_qiskit.utils import (
    qiskit_circ_to_itn_circ_2d, extract_cx_gates,
)

jl.seval("using ITensorNetworksQiskit")

# Any Julia functions from outside our package should be added here
jl.seval("using ITensorNetworks: siteinds")

cmap = CouplingMap().from_heavy_hex(7)
print(f"Created heavy-hex graph with {cmap.size()} qubits")
backend = GenericBackendV2(cmap.size(), coupling_map=cmap)
graph = backend.coupling_map.get_edges()
# Remove duplicates with opposite direction
graph = [list(s) for s in set([frozenset(item) for item in graph])]

qc = QuantumCircuit(backend.num_qubits)
num_layers = 10
for i in range(num_layers):
    for edge in graph:
        qc.h(edge[0])
        qc.h(edge[1])
        qc.cx(edge[0], edge[1])
        qc.ry(random.random() * np.pi, edge[0])
        qc.ry(random.random() * np.pi, edge[1])

qc = transpile(qc, basis_gates=["rx", "ry", "rz", "cx"], backend=backend)
plot_circuit_layout(qc, backend).show()

# convert circuit to required ITN format
itn_circ = qiskit_circ_to_itn_circ_2d(qc)

# build ITN graph from the Qiskit circuit
graph_string = extract_cx_gates(itn_circ)
g = jl.build_graph_from_gates(jl.seval(graph_string))
s = jl.siteinds("S=1/2", g)

# set a desired maximum bond dimension
chi = 50
start_time = datetime.now()

# run simulation
# extract output MPS and belief propagation cache (bpc)
psi, bpc = jl.tn_from_circuit(itn_circ, chi, s)
t = datetime.now() - start_time
print(t)

print("***** ITN results *****")
itn_overlap = jl.overlap_with_zero(psi, s)
itn_eval = jl.pauli_expectation("Z", psi, [1, 2], bpc)
itn_rdm = jl.get_first_edge_rdm_2d(psi, bpc, g)
print(f"Overlap with zero state: {itn_overlap}")
print(f"σz expectation value of sites 1 and 2: {itn_eval}")
print(f"2-qubit RDM of sites of first edge: {itn_rdm}")
print("\n")
