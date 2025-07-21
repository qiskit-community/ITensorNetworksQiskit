from qiskit import QuantumCircuit
from qiskit.circuit import Qubit


def jl_qubit_int_from_qiskit_qubit_obj(qubit: Qubit):
    return qubit._index + 1


def qiskit_circ_to_itn_circ(qc: QuantumCircuit):
    gate_formats = {
        "u": lambda qubits,
                    params: f'("Rn", [({qubits[0]}, 1)], (θ = {params[0]}, ϕ = {params[1]}, λ = {params[2]}))',
        "rx": lambda qubits, params: f'("Rx", [({qubits[0]}, 1)], (θ = {params[0]},))',
        "ry": lambda qubits, params: f'("Ry", [({qubits[0]}, 1)], (θ = {params[0]},))',
        "rz": lambda qubits, params: f'("Rz", [({qubits[0]}, 1)], (θ = {params[0]},))',
        "t": lambda qubits, _: f'("T", [({qubits[0]}, 1)])',
        "cx": lambda qubits, _: f'("CX", [({qubits[0]}, 1), ({qubits[1]}, 1)])',
        "swap": lambda qubits, _: f'("SWAP", [({qubits[0]}, 1), ({qubits[1]}, 1)])',
    }

    gates = []

    for qiskit_gate in qc:
        name = qiskit_gate.operation.name
        qubits = [
            jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[i])
            for i in range(len(qiskit_gate.qubits))
        ]
        params = qiskit_gate.operation.params

        if name in gate_formats:
            gates.append(gate_formats[name](qubits, params))
        else:
            raise ValueError(f"Unknown gate: {name}")

    return "[" + ", ".join(gates) + "]"


# This is the same function as above but the gates are needed a different form. Instead of the
# index listed as [({qubit}, 1)] it needs to be [{qubit}].
def qiskit_circ_to_itn_circ_2d(qc: QuantumCircuit, qmap: dict = None):
    qmap = {i: i for i in range(1, qc.num_qubits + 1)} if qmap is None else qmap
    gate_formats = {
        "u": lambda qubits,
                    params: f'("Rn", [{qmap[qubits[0]]}], (θ = {params[0]}, ϕ = {params[1]}, λ = {params[2]}))',
        "rx": lambda qubits, params: f'("Rx", [{qmap[qubits[0]]}], {params[0]})',
        "ry": lambda qubits, params: f'("Ry", [{qmap[qubits[0]]}], {params[0]})',
        "rz": lambda qubits, params: f'("Rz", [{qmap[qubits[0]]}], {params[0]})',
        "t": lambda qubits, _: f'("T", [{qmap[qubits[0]]}])',
        "cx": lambda qubits, _: f'("CX", [{qmap[qubits[0]]}, {qmap[qubits[1]]}])',
        "swap": lambda qubits, _: f'("SWAP", [{qmap[qubits[0]]}, {qmap[qubits[1]]}])',
    }

    gates = []

    for qiskit_gate in qc:
        name = qiskit_gate.operation.name
        qubits = [
            jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[i])
            for i in range(len(qiskit_gate.qubits))
        ]
        params = qiskit_gate.operation.params

        if name in gate_formats:
            gates.append(gate_formats[name](qubits, params))
        else:
            raise ValueError(f"Unknown gate: {name}")

    return "[" + ", ".join(gates) + "]"
