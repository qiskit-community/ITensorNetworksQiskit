import random
from datetime import datetime

import numpy as np
from juliacall import Main as jl
from qiskit import transpile, QuantumCircuit
from qiskit.providers.fake_provider import Fake127QPulseV1

from itensornetworks_qiskit.utils import (
    qiskit_circ_to_itn_circ_2d, prepare_graph_for_itn,
)

jl.seval("using ITensorNetworksQiskit")
jl.seval("using ITensors: siteinds")

backend = Fake127QPulseV1()
graph = backend.configuration().coupling_map

qc = QuantumCircuit(127)
for edge in graph:
    qc.h(edge[0])
    qc.h(edge[1])
    qc.cx(edge[0], edge[1])
    qc.ry(random.random() * np.pi, edge[0])
    qc.ry(random.random() * np.pi, edge[1])

qc = transpile(qc, basis_gates=["rx", "ry", "rz", "cx"])

# generate circuit in required ITN format
itn_circ = qiskit_circ_to_itn_circ_2d(qc)

# build ITN graph from Qiskit
graph_string = prepare_graph_for_itn(itn_circ)
g = jl.build_graph_from_gates(jl.seval(graph_string))

# derive site indices list and other params from graph
s = jl.siteinds("S=1/2", g)
chi = 100
start_time = datetime.now()
n_layers = 3
# run simulation
# extract output MPS and belief propagation cache (bpc)
psi, bpc = jl.tn_from_circuit(itn_circ, chi, s, n_layers)
t = datetime.now() - start_time
print(t)

print("ITN results")
itn_overlap = jl.overlap_with_zero(psi, s)
itn_eval = jl.sigmaz_expectation_2d(psi, [1, 2])
itn_rdm = jl.get_first_edge_rdm_2d(psi, bpc, g)
print(f"Overlap with zero state: {itn_overlap}")
print(f"σz expectation value of sites 1 and 2: {itn_eval}")
print(f"2-qubit RDM of sites 0 and 6: {itn_rdm}")
print("\n")
