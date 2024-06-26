from juliacall import Main as jl
from qiskit import QuantumCircuit
from qiskit.circuit import Qubit

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

print(qc)


def jl_qubit_int_from_qiskit_qubit_obj(qubit: Qubit):
    return qubit._index + 1


gates = '['

for qiskit_gate in qc:
    if qiskit_gate.operation.name == 'u':
        qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
        theta, phi, lam = qiskit_gate.operation.params
        gates += f'("Rn", [({qubit}, 1)], (θ = {theta}, ϕ = {phi}, λ = {lam})), '
    elif qiskit_gate.operation.name == 'rx':
        qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
        theta, = qiskit_gate.operation.params
        gates += f'("Rx", [({qubit}, 1)], (θ = {theta},)), '
    elif qiskit_gate.operation.name == 'ry':
        qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
        theta, = qiskit_gate.operation.params
        gates += f'("Ry", [({qubit}, 1)], (θ = {theta},)), '
    elif qiskit_gate.operation.name == 'rz':
        qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
        theta, = qiskit_gate.operation.params
        gates += f'("Rz", [({qubit}, 1)], (θ = {theta},)), '
    elif qiskit_gate.operation.name == 't':
        qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
        gates += f'("T", [({qubit}, 1)]), '
    elif qiskit_gate.operation.name == 'cx':
        ctrl = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
        tgt = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[1])
        gates += f'("CX", [({ctrl}, 1), ({tgt}, 1)]), '
    elif qiskit_gate.operation.name == 'swap':
        ctrl = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
        tgt = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[1])
        gates += f'("SWAP", [({ctrl}, 1), ({tgt}, 1)]), '
    else:
        raise ValueError('Unknown gate')

gates += ']'

# gates = '[("X", [(1, 1)]), ("CX", [(1, 1), (2, 1)]), ("Rx", [(2, 1)], (θ = 0.5,)), ("Rn", [(3, 1)], (θ = 0.5, ϕ = 0.2, λ = 1.2)), ("√SWAP", [(3, 1), (4, 1)]), ("T", [(4, 1)])]'
jl.seval(
    f"""include("./src/ITensorNetworksQiskit.jl");
    circuitMPS({n},{gates})"""
)
