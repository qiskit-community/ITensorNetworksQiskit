"""Example building a small 2D circuit with three layers of random gates, generating the tensor
network representation using ITN and then validating observables against Qiskit state vector
simulation"""

import random
from datetime import datetime

import numpy as np
from juliacall import Main as jl
from matplotlib import pyplot as plt
from qiskit import transpile, QuantumCircuit
from qiskit.circuit.library import ZGate
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.quantum_info import partial_trace, Statevector, concurrence, DensityMatrix
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_circuit_layout

from itensornetworks_qiskit.graph import extract_cx_gates
from itensornetworks_qiskit.utils import qiskit_circ_to_itn_circ_2d

jl.seval("using ITensorNetworksQiskit")

# Any Julia functions from outside our package should be added here
jl.seval("using ITensorNetworks: siteinds, maxlinkdim")

cmap = CouplingMap().from_heavy_hex(3)
print(f"Created heavy-hex graph with {cmap.size()} qubits")
backend = GenericBackendV2(cmap.size(), coupling_map=cmap)
graph = backend.coupling_map.get_edges()
# Remove duplicates with opposite direction
graph = [list(s) for s in set([frozenset(item) for item in graph])]

# Optional seed to make the example deterministic
random.seed(1)

qc = QuantumCircuit(backend.num_qubits)
num_layers = 3

itn_evals = []
qiskit_evals = []

for _ in range(num_layers):
    for edge in graph:
        qc.h(edge[0])
        qc.h(edge[1])
        qc.cx(edge[0], edge[1])
        qc.ry(random.random() * np.pi, edge[0])
        qc.ry(random.random() * np.pi, edge[1])

    qc = transpile(qc, basis_gates=["rx", "ry", "rz", "cx"], backend=backend)

    # generate circuit in required ITN format
    itn_circ = qiskit_circ_to_itn_circ_2d(qc)

    # build ITN graph from Qiskit
    graph_string = extract_cx_gates(itn_circ)
    g = jl.build_graph_from_gates(jl.seval(graph_string))

    # derive site indices list and other params from graph
    s = jl.siteinds("S=1/2", g)
    chi = 50
    start_time = datetime.now()

    psi, bpc, errors = jl.tn_from_circuit(itn_circ, chi, s)
    print("Maximum bond dimension", jl.maxlinkdim(psi))
    print("Estimated final state fidelity:", np.prod(1 - np.array(errors)))
    t = datetime.now() - start_time
    print("Time taken to simulate layer:", t)

    itn_overlap = jl.overlap_with_zero(psi, s)
    itn_eval = jl.pauli_expectation("Z", psi, list(range(1, 6)), bpc)
    itn_evals.append(itn_eval)

    itn_rdm = jl.get_first_edge_rdm_2d(psi, bpc, g)

    # Statevector simulation with Qiskit
    sv = Statevector(qc)
    qiskit_overlap = (np.abs(sv[0]))**2
    qiskit_eval = [sv.expectation_value(ZGate(), [i]) for i in range(5)]
    qiskit_evals.append(qiskit_eval)
    qubits_to_trace = [q for q in range(backend.num_qubits) if q not in graph[0]]
    qiskit_rdm = partial_trace(sv, qubits_to_trace)

    # Numerically check both methods give same values
    np.testing.assert_almost_equal(itn_overlap, qiskit_overlap, decimal=5)
    np.testing.assert_almost_equal(itn_eval, qiskit_eval, decimal=5)
    converted_itn_rdm = DensityMatrix(np.array(itn_rdm))
    converted_qiskit_rdm = DensityMatrix(np.array(qiskit_rdm))
    # Density matrices differ by 4 elements, but entanglement measures come out the same
    np.testing.assert_almost_equal(concurrence(converted_itn_rdm),
                                   concurrence(converted_qiskit_rdm),
                                   decimal=5)

qc.draw(output="mpl", fold=-1, filename="validate_small_heavy_hex_circ.pdf")
plt.close()
plot_circuit_layout(qc, backend).show()
plt.plot(range(1, num_layers + 1), itn_evals, "x", markersize=8)
plt.gca().set_prop_cycle(None)
plt.plot(range(1, num_layers + 1), qiskit_evals, "^", markersize=8)
plt.xticks(range(1, num_layers + 1))
plt.plot([], [], "x", color="black", label='ITNQ belief propagation')
plt.plot([], [], "^", color="black", label='Qiskit statevector')
plt.ylabel(r"$\langle \sigma^z \rangle$")
plt.xlabel("Number of random circuit layers")
plt.legend()
plt.savefig("validate_small_heavy_hex_sz.pdf")
