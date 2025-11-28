"""Example building a large heavy-hex circuit with 5 repeated layers of random gates,
generating the tensor network representation using ITN and then computing observables"""

import random
from datetime import datetime

import numpy as np
from juliacall import Main as jl
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import SparsePauliOp
from qiskit.visualization import plot_circuit_layout
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

from itensornetworks_qiskit.convert import (
    circuit_description,
    observable_description,
    SUPPORTED_GATES,
)
from itensornetworks_qiskit.graph import graph_from_edges, graph_to_grid

# Import any julia dependencies we are calling directly
jl.seval("using ITensorNetworksQiskit")
jl.seval("using TensorNetworkQuantumSimulator")

backend = FakeSherbrooke()
n_qubits = backend.num_qubits
cmap = backend.coupling_map
print(f"Created heavy-hex graph from {backend.name} with {cmap.size()} qubits")

# Remove duplicates with opposite direction
connectivity = [list(s) for s in set([frozenset(item) for item in cmap.get_edges()])]

qc = QuantumCircuit(backend.num_qubits)
num_layers = 5
for i in range(num_layers):
    for edge in connectivity:
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

plot_circuit_layout(
    qc, backend, qubit_coordinates=[qmap[i][1] for i in range(n_qubits)]
).show()

# Set tensor network truncation parameters
chi = 4
cutoff = 1e-12

start_time = datetime.now()
psi_bpc, errors = jl.tn_from_circuit(circuit, qmap, edges, chi, cutoff)
psi_bpc = jl.rescale(psi_bpc)
psi = jl.network(psi_bpc)
print("Estimated final state fidelity:", np.prod(1 - np.array(errors)))

t = datetime.now() - start_time
print(t)

print("***** ITN results *****")
# Create the |00..0> state using the same graph and site indices
psi_zero = jl.zerostate(psi.tensornetwork.graph, psi.siteinds)
# Compute the overlap |<0|psi>|^2
itn_overlap = abs(jl.inner(psi_zero, psi, alg="bp")) ** 2
print(f"Overlap with zero state: {itn_overlap}")

# Compute Z expectation values of an observable on qubits 1 and 2 of the qiskit circuit.
obs = SparsePauliOp.from_sparse_list([("Z", [q], 1.0) for q in [1, 2]], qc.num_qubits)
obs_jl = jl.translate_observable(observable_description(obs), qmap)
z_eval = np.real(jl.sum(jl.expect(psi_bpc, obs_jl)))
print(f"σz expectation value of sites 1 + 2: {z_eval}")

# And also compute a multi-qubit observable
obs = SparsePauliOp.from_sparse_list([("XXX", [0, 1, 2], 1.0)], qc.num_qubits)
obs_jl = jl.translate_observable(observable_description(obs), qmap)
z_eval = np.real(jl.sum(jl.expect(psi_bpc, obs_jl)))
print(f"σxxx expectation value of sites 1, 2 and 3: {z_eval}")
