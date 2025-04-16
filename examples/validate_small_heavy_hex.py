"""Example building a large 2D circuit with one layer of random gates, generating the tensor network
 representation using ITN and then computing observables"""

import random
from datetime import datetime

import numpy as np
from juliacall import Main as jl
from qiskit import transpile, QuantumCircuit
from qiskit.circuit.library import ZGate
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.quantum_info import partial_trace, Statevector, concurrence, DensityMatrix
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_circuit_layout

from itensornetworks_qiskit.utils import (
    qiskit_circ_to_itn_circ_2d, prepare_graph_for_itn,
)

jl.seval("using ITensorNetworksQiskit")

# Any Julia functions from outside our package should be added here
jl.seval("using ITensorNetworks: siteinds")

cmap = CouplingMap().from_heavy_hex(3)
backend = GenericBackendV2(cmap.size(), coupling_map=cmap)
graph = backend.coupling_map.get_edges()
# Remove duplicates with opposite direction
graph = [list(s) for s in set([frozenset(item) for item in graph])]

# Optional to make the example deterministic
random.seed(1)

qc = QuantumCircuit(backend.num_qubits)
for _ in range(3):
    for edge in graph:
        qc.h(edge[0])
        qc.h(edge[1])
        qc.cx(edge[0], edge[1])
        qc.ry(random.random() * np.pi, edge[0])
        qc.ry(random.random() * np.pi, edge[1])

qc = transpile(qc, basis_gates=["rx", "ry", "rz", "cx"], backend=backend)
plot_circuit_layout(qc, backend).show()
qc.draw(output="mpl").show()

# generate circuit in required ITN format
itn_circ = qiskit_circ_to_itn_circ_2d(qc)

# build ITN graph from Qiskit
graph_string = prepare_graph_for_itn(itn_circ)
g = jl.build_graph_from_gates(jl.seval(graph_string))

# derive site indices list and other params from graph
s = jl.siteinds("S=1/2", g)
chi = 50
start_time = datetime.now()
n_layers = 1
# run simulation
# extract output MPS and belief propagation cache (bpc)
psi, bpc = jl.tn_from_circuit(itn_circ, chi, s, n_layers)
t = datetime.now() - start_time
print(t)

print("***** ITN results *****")
itn_overlap = jl.overlap_with_zero(psi, s)
itn_eval = jl.sigmaz_expectation_2d(psi, list(range(1, backend.num_qubits + 1)), bpc)
itn_rdm = jl.get_first_edge_rdm_2d(psi, bpc, g)
print(f"Overlap with zero state: {itn_overlap}")
print(f"σz expectation value of sites 1 and 2: {itn_eval}")
print(f"2-qubit RDM of sites of first edge: {itn_rdm}")
print("\n")

print("***** Qiskit results *****")
sv = Statevector(qc)
qiskit_overlap = (np.abs(sv[0]))**2
qiskit_eval = [sv.expectation_value(ZGate(), [i]) for i in range(backend.num_qubits)]
qubits_to_trace = [q for q in range(backend.num_qubits) if q not in graph[0]]
qiskit_rdm = partial_trace(sv, qubits_to_trace)
print(f"Overlap with zero state: {qiskit_overlap}")
print(f"σz expectation value of sites 1 and 2: {qiskit_eval}")
print(f"2-qubit RDM of sites 1 and 2: {qiskit_rdm}")

np.testing.assert_almost_equal(itn_overlap, qiskit_overlap)
np.testing.assert_almost_equal(itn_eval, qiskit_eval)
converted_itn_rdm = DensityMatrix(np.array(itn_rdm))
converted_qiskit_rdm = DensityMatrix(np.array(qiskit_rdm))
# Density matrices differ by 4 elements, but entanglement measures come out the same
np.testing.assert_almost_equal(concurrence(converted_itn_rdm), concurrence(converted_qiskit_rdm))
