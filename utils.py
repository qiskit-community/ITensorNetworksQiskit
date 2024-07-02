from qiskit import QuantumCircuit
from qiskit.circuit import Qubit


def jl_qubit_int_from_qiskit_qubit_obj(qubit: Qubit):
    return qubit._index + 1


def qiskit_circ_to_itn_circ(qc: QuantumCircuit):
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
    return gates
