import numpy as np
from juliacall import Main as jl
from qiskit.circuit.library import ZGate
from qiskit.quantum_info import Statevector

from itensornetworks_qiskit.utils import qiskit_circ_to_it_circ

jl.seval("using ITensorNetworksQiskit")

from qiskit import transpile
from qiskit.circuit.random import random_circuit

n = 5
cmap = [[j, j + 1] for j in range(n - 1)]
qc = transpile(
    random_circuit(n, depth=2, max_operands=2, seed=0),
    basis_gates=["rx", "ry", "rz", "cx"],
    coupling_map=cmap,
)

gates = qiskit_circ_to_it_circ(qc)
s = jl.generate_siteindices_itensors(n)
psi = jl.mps_from_circuit_itensors(n, gates, 10, s)

print("***** ITensors results *****")
itn_overlap = jl.overlap_with_zero_itensors(n, psi, s)
itn_eval = jl.sigmaz_expectation_itensors(psi, [1, 2])
print(f"Overlap with zero state: {itn_overlap}")
print(f"σz expectation value of sites 1 and 2: {itn_eval}")
print("\n")

print("***** Qiskit results *****")
sv = Statevector(qc)
qiskit_overlap = (np.abs(sv[0]))**2
qiskit_eval = [sv.expectation_value(ZGate(), [i]) for i in range(2)]
print(f"Overlap with zero state: {qiskit_overlap}")
print(f"σz expectation value of sites 1 and 2: {qiskit_eval}")

np.testing.assert_almost_equal(itn_overlap, qiskit_overlap)
np.testing.assert_almost_equal(itn_eval, qiskit_eval)
