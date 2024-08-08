import numpy as np
from juliacall import Main as jl
from qiskit.circuit.library import ZGate
from qiskit.quantum_info import partial_trace, Statevector, concurrence, DensityMatrix

from itensornetworks_qiskit.utils import qiskit_circ_to_itn_circ

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

itn_circ = qiskit_circ_to_itn_circ(qc)
s = jl.generate_siteindices(n)
chi = 10
psi, bpc = jl.mps_from_circuit(n, itn_circ, chi, s)

print("ITN results")
itn_overlap = jl.overlap_with_zero(psi, s)
itn_eval = jl.sigmaz_expectation(psi, [1, 2])
itn_rdm = jl.two_site_rdm(psi, bpc, 1, 2)
print(f"Overlap with zero state: {itn_overlap}")
print(f"σz expectation value of sites 1 and 2: {itn_eval}")
print(f"2-qubit RDM of sites 1 and 2: {itn_rdm}")
print("\n")

print("Qiskit results")
sv = Statevector(qc)
qiskit_overlap = (np.abs(sv[0]))**2
qiskit_eval = [sv.expectation_value(ZGate(), [i]) for i in range(2)]
qiskit_rdm = partial_trace(sv, [i for i in range(2, n)])
print(f"Overlap with zero state: {qiskit_overlap}")
print(f"σz expectation value of sites 1 and 2: {qiskit_eval}")
print(f"2-qubit RDM of sites 1 and 2: {qiskit_rdm}")

np.testing.assert_almost_equal(itn_overlap, qiskit_overlap)
np.testing.assert_almost_equal(itn_eval, qiskit_eval)
converted_itn_rdm = DensityMatrix(np.array(itn_rdm))
converted_qiskit_rdm = DensityMatrix(np.array(qiskit_rdm))
# Density matrices differ by 4 elements, but entanglement measures come out the same
np.testing.assert_almost_equal(concurrence(converted_itn_rdm), concurrence(converted_qiskit_rdm))
