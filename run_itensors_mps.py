from juliacall import Main as jl
from qiskit import QuantumCircuit

from itensornetworks_qiskit.utils import qiskit_circ_to_it_circ

jl.seval("using ITensorNetworksQiskit")

n = 4
qc = QuantumCircuit(n)

for i in range(n):
    qc.u(1., 2., 3., i)
for i in range(n - 1):
    qc.cx(i, i + 1)
for i in range(n):
    qc.rx(4., i)
    qc.ry(5., i)
    qc.rz(6., i)
for i in range(n - 1):
    qc.swap(i, i + 1)
for i in range(n):
    qc.t(i)

gates = qiskit_circ_to_it_circ(qc)
s = jl.generate_siteindices_itensors(n)
print(jl.mps_from_circuit_itensors(n, gates, 10, s))
