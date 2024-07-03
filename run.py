from juliacall import Main as jl
from qiskit import QuantumCircuit
from qiskit.circuit import Qubit

from utils import qiskit_circ_to_itn_circ

jl.seval("using ITensorNetworksQiskit")

n = 4
qc = QuantumCircuit(n)

for i in range(n):
    qc.u(1., 2., 3., i)
    # NB: currently, requirement of julia code being used is that two qubits gates only act on
    # nearest neighbour qubits (non-cyclic)
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

gates = qiskit_circ_to_itn_circ(qc)
jl.circuitMPS(n, gates)
