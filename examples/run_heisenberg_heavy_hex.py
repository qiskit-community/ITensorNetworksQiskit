"""Example building a large 2D circuit with two layers of a Heisenberg-like Trotter step,
generating the tensor network representation using ITN and then computing observables"""

from datetime import datetime

import numpy as np
from juliacall import Main as jl
from qiskit import transpile, QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_circuit_layout

from itensornetworks_qiskit.utils import (
    qiskit_circ_to_itn_circ_2d, prepare_graph_for_itn,
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

jxx = 1.0
jyy = 1.0
jzz = 1.0

qc = QuantumCircuit(115)
qc.x(range(115)[::2])


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


for _ in range(2):
    trotter_step(qc)

qc = transpile(qc, basis_gates=["rx", "ry", "rz", "cx"], optimization_level=3, backend=backend)
qc.draw(output='mpl', filename='heisenberg_heavy_hex.pdf', fold=-1)

# convert circuit to required ITN format
itn_circ = qiskit_circ_to_itn_circ_2d(qc)

# build ITN graph from the Qiskit circuit
graph_string = prepare_graph_for_itn(itn_circ)
g = jl.build_graph_from_gates(jl.seval(graph_string))

s = jl.siteinds("S=1/2", g)

# set a desired maximum bond dimension
chi = 100
start_time = datetime.now()

# Here we define only 1 layer since the circuit is not entirely a repeated structure (due to bit
# flip state preparation)
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
