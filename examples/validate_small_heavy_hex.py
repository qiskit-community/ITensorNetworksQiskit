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
from qiskit.quantum_info import (
    partial_trace,
    Statevector,
    DensityMatrix,
    SparsePauliOp,
)
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_circuit_layout

from qiskit_tnqs.convert import (
    SUPPORTED_GATES,
    circuit_description,
    observable_description,
)
from qiskit_tnqs.graph import graph_to_grid, graph_from_edges
from qiskit_tnqs.observables import rdm

jl.seval("using QiskitTNQS")
jl.seval("using QiskitTNQS: rdm")
jl.seval("using TensorNetworkQuantumSimulator")

cmap = CouplingMap().from_heavy_hex(3)
print(f"Created heavy-hex graph with {cmap.size()} qubits")
backend = GenericBackendV2(cmap.size(), coupling_map=cmap)
graph = backend.coupling_map.get_edges()
# Remove duplicates with opposite direction
graph = [list(s) for s in set([frozenset(item) for item in graph])]

# Optional seed to make the example deterministic
random.seed(2)

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

    qc = transpile(qc, backend=backend, basis_gates=list(SUPPORTED_GATES))

    # Convert the circuit to the form expected by TNQS
    circuit, edges = circuit_description(qc)

    # Get the necessary mapping from qiskit qubit indices to 2D coordinate grid
    qmap = graph_to_grid(graph_from_edges(edges))

    # Set tensor network truncation parameters
    chi = 50
    cutoff = 1e-12
    start_time = datetime.now()

    psi_bpc, errors = jl.tn_from_circuit(circuit, qmap, edges, chi, cutoff)
    print("Estimated final state fidelity:", np.prod(1 - np.array(errors)))
    t = datetime.now() - start_time
    print("Time taken to simulate layer:", t)

    # Get the overlap with the |00...0> state
    psi_bpc = jl.rescale(psi_bpc)
    psi = jl.network(psi_bpc)
    psi_zero = jl.zerostate(psi.tensornetwork.graph, psi.siteinds)
    itn_overlap = abs(jl.inner(psi_zero, psi, alg="bp"))**2

    # Get expectation values
    obs = SparsePauliOp.from_sparse_list(
        [("Z", [q], 1.0) for q in range(5)], qc.num_qubits
    )
    obs_jl = jl.translate_observable(observable_description(obs), qmap)
    itn_eval = np.real(jl.expect(psi_bpc, obs_jl))
    itn_evals.append(itn_eval)

    # Obtain the 2-qubit RDM of the first edge
    qmap_dict = {qiskit_index: itn_index for (qiskit_index, itn_index) in qmap}
    first_edge_qiskit = graph[0]
    first_edge_itn = tuple(qmap_dict[q] for q in first_edge_qiskit)
    itn_rdm = rdm(psi_bpc, first_edge_itn, alg="bp")

    # Statevector simulation with Qiskit
    sv = Statevector(qc)
    qiskit_overlap = (np.abs(sv[0]))**2
    qiskit_eval = [sv.expectation_value(ZGate(), [i]) for i in range(5)]
    qiskit_evals.append(qiskit_eval)
    qubits_to_trace = [q for q in range(backend.num_qubits) if q not in graph[0]]
    qiskit_rdm = partial_trace(sv, qubits_to_trace)

    # Numerically check both methods give same values
    np.testing.assert_almost_equal(itn_overlap, qiskit_overlap, decimal=3)
    np.testing.assert_almost_equal(itn_eval, qiskit_eval, decimal=3)

    converted_itn_rdm = DensityMatrix(itn_rdm)

    np.testing.assert_almost_equal(converted_itn_rdm.data, qiskit_rdm.data, decimal=3)

# Plot the <Z> expectation values to see agreement
qc.draw(output="mpl", fold=-1, filename="validate_small_heavy_hex_circ.pdf")
plt.close()
plot_circuit_layout(qc, backend).show()
plt.plot(range(1, num_layers + 1), itn_evals, "x", markersize=8)
plt.gca().set_prop_cycle(None)
plt.plot(range(1, num_layers + 1), qiskit_evals, "^", markersize=8)
plt.xticks(range(1, num_layers + 1))
plt.plot([], [], "x", color="black", label="ITNQ belief propagation")
plt.plot([], [], "^", color="black", label="Qiskit statevector")
plt.ylabel(r"$\langle \sigma^z \rangle$")
plt.xlabel("Number of random circuit layers")
plt.legend()
plt.savefig("validate_small_heavy_hex_sz.pdf")
plt.show()
