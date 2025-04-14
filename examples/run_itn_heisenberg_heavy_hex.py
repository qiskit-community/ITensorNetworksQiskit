"""Example building a large 2D circuit with one layer of a Heisenberg-like Trotter step,
generating the tensor network representation using ITN and then computing observables"""

from datetime import datetime

import numpy as np
from juliacall import Main as jl
from qiskit import transpile, QuantumCircuit
from qiskit.providers.fake_provider import Fake127QPulseV1

from itensornetworks_qiskit.utils import (
    qiskit_circ_to_itn_circ_2d, prepare_graph_for_itn,
)

jl.seval("using ITensorNetworksQiskit")

# Any Julia functions from outside our package should be added here
jl.seval("using ITensorNetworks: siteinds")

backend = Fake127QPulseV1()
graph = backend.configuration().coupling_map
# Remove duplicates with opposite direction
graph = [list(s) for s in set([frozenset(item) for item in graph])]

jxx = 1.0
jyy = 1.0
jzz = 1.0

qc = QuantumCircuit(127)
qc.x(range(127)[::2])


def trotter_step(qc):
    for edge in graph:
        if edge[0] % 2 == 0:
            qc.rz(-np.pi / 2.0, edge[1])
            qc.cx(edge[1], edge[0])
            qc.rz(np.pi / 2 - jzz / 2, edge[0])
            qc.ry(jxx / 2 - np.pi / 2, edge[1])
            qc.cx(edge[0], edge[1])
            qc.ry(np.pi / 2 - jyy / 2, edge[1])
            qc.cx(edge[1], edge[0])
            qc.rz(np.pi / 2.0, edge[0])
        else:
            qc.rz(-np.pi / 2.0, edge[1])
            qc.cx(edge[1], edge[0])
            qc.rz(np.pi / 2 - jzz / 2, edge[0])
            qc.ry(jxx / 2 - np.pi / 2, edge[1])
            qc.cx(edge[0], edge[1])
            qc.ry(np.pi / 2 - jyy / 2, edge[1])
            qc.cx(edge[1], edge[0])
            qc.rz(np.pi / 2.0, edge[0])


for _ in range(1):
    trotter_step(qc)

qc = transpile(qc, basis_gates=["rx", "ry", "rz", "cx"], optimization_level=3)
# qc.draw(output='mpl', filename='heisenberg_heavy_hex.pdf', fold=-1)

# generate circuit in required ITN format
itn_circ = qiskit_circ_to_itn_circ_2d(qc)

# build ITN graph from Qiskit
graph_string = prepare_graph_for_itn(itn_circ)
g = jl.build_graph_from_gates(jl.seval(graph_string))

# derive site indices list and other params from graph
s = jl.siteinds("S=1/2", g)
chi = 100
start_time = datetime.now()
n_layers = 1
# run simulation
# extract output MPS and belief propagation cache (bpc)
psi, bpc = jl.tn_from_circuit(itn_circ, chi, s, n_layers)
t = datetime.now() - start_time
print(t)

print("***** ITN results *****")
itn_overlap = jl.overlap_with_zero(psi, s)
itn_eval = jl.sigmaz_expectation_2d(psi, [1, 2])
print(f"Overlap with zero state: {itn_overlap}")
print(f"σz expectation value of sites 1 and 2: {itn_eval}")
print("\n")
