import io
import re
import sys

from qiskit import QuantumCircuit
from qiskit.circuit import Qubit


def jl_qubit_int_from_qiskit_qubit_obj(qubit: Qubit):
    return qubit._index + 1


def qiskit_circ_to_itn_circ(qc: QuantumCircuit):
    gate_formats = {
        "u": lambda qubits, params: f'("Rn", [({qubits[0]}, 1)], (θ = {params[0]}, ϕ = {params[1]}, λ = {params[2]}))',
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
# index listed as [({qubit}, 1)] it needs to be [({qubit}),].
def qiskit_circ_to_itn_circ_2d(qc: QuantumCircuit):
    gate_formats = {
        "u": lambda qubits, params: f'("Rn", [({qubits[0]},)], (θ = {params[0]}, ϕ = {params[1]}, λ = {params[2]}))',
        "rx": lambda qubits, params: f'("Rx", [({qubits[0]},)], (θ = {params[0]},))',
        "ry": lambda qubits, params: f'("Ry", [({qubits[0]},)], (θ = {params[0]},))',
        "rz": lambda qubits, params: f'("Rz", [({qubits[0]},)], (θ = {params[0]},))',
        "t": lambda qubits, _: f'("T", [({qubits[0]},)])',
        "cx": lambda qubits, _: f'("CX", [({qubits[0]},), ({qubits[1]},)])',
        "swap": lambda qubits, _: f'("SWAP", [({qubits[0]},), ({qubits[1]},)])',
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

# Again, this is very similar to the functions as above but the gates need to be a different form.
# Instead of the index listed as [({qubit}, 1)] or [({qubit}),] it needs to be simply {qubit}
def qiskit_circ_to_it_circ(qc: QuantumCircuit):
    gates = '['
    for qiskit_gate in qc:
        if qiskit_gate.operation.name == 'u':
            qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            theta, phi, lam = qiskit_gate.operation.params
            gates += f'("Rn", {qubit}, (θ = {theta}, ϕ = {phi}, λ = {lam})), '
        elif qiskit_gate.operation.name == 'rx':
            qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            theta, = qiskit_gate.operation.params
            gates += f'("Rx", {qubit}, (θ = {theta},)), '
        elif qiskit_gate.operation.name == 'ry':
            qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            theta, = qiskit_gate.operation.params
            gates += f'("Ry", {qubit}, (θ = {theta},)), '
        elif qiskit_gate.operation.name == 'rz':
            qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            theta, = qiskit_gate.operation.params
            gates += f'("Rz", {qubit}, (θ = {theta},)), '
        elif qiskit_gate.operation.name == 't':
            qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            gates += f'("T", {qubit}), '
        elif qiskit_gate.operation.name == 'cx':
            ctrl = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            tgt = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[1])
            gates += f'("CX", {ctrl},{tgt}), '
        elif qiskit_gate.operation.name == 'swap':
            ctrl = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            tgt = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[1])
            gates += f'("SWAP", {ctrl},{tgt}), '
        else:
            raise ValueError('Unknown gate')

    gates += ']'
    return gates

def extract_itn_graph(g):
    output_capture = io.StringIO()
    sys.stdout = output_capture
    print(g)
    sys.stdout = sys.__stdout__
    julia_output = output_capture.getvalue()
    output_capture.close()
    edges_str = julia_output.split(" edge(s):")[1].strip()
    edge_pattern = re.compile(r"\((\d+),\) => \((\d+),\)")
    edges = edge_pattern.findall(edges_str)
    edges_tuples = [(int(x)-1, int(y)-1) for x, y in edges]
    return edges_tuples
