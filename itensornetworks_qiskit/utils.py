import io
import re
import sys

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

# This is the same function as above but the gates are needed a different form. Instead of the
# index listed as [({qubit}, 1)] it needs to be [({qubit}),].
def qiskit_circ_to_itn_circ_2d(qc: QuantumCircuit):
    gates = '['
    for qiskit_gate in qc:
        if qiskit_gate.operation.name == 'u':
            qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            theta, phi, lam = qiskit_gate.operation.params
            gates += f'("Rn", [({qubit},)], (θ = {theta}, ϕ = {phi}, λ = {lam})), '
        elif qiskit_gate.operation.name == 'rx':
            qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            theta, = qiskit_gate.operation.params
            gates += f'("Rx", [({qubit},)], (θ = {theta},)), '
        elif qiskit_gate.operation.name == 'ry':
            qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            theta, = qiskit_gate.operation.params
            gates += f'("Ry", [({qubit},)], (θ = {theta},)), '
        elif qiskit_gate.operation.name == 'rz':
            qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            theta, = qiskit_gate.operation.params
            gates += f'("Rz", [({qubit},)], (θ = {theta},)), '
        elif qiskit_gate.operation.name == 't':
            qubit = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            gates += f'("T", [({qubit},)]), '
        elif qiskit_gate.operation.name == 'cx':
            ctrl = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            tgt = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[1])
            gates += f'("CX", [({ctrl},), ({tgt},)]), '
        elif qiskit_gate.operation.name == 'swap':
            ctrl = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[0])
            tgt = jl_qubit_int_from_qiskit_qubit_obj(qiskit_gate.qubits[1])
            gates += f'("SWAP", [({ctrl},), ({tgt},)]), '
        else:
            raise ValueError('Unknown gate')

    gates += ']'
    return gates

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
