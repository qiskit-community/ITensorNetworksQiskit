from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp


def circuit_description(
    qc: QuantumCircuit,
) -> tuple[
    tuple[tuple[str, tuple[int, ...], tuple[float, ...]], ...],
    tuple[tuple[int, int], ...],
]:
    """
    Creates a necessary description of a qiskit circuit to be used in TensorNetworkQuantumSimulator.
    For now only 2 qubit gates and paulis are supported.
    Args:
        qc: A Quantum circuit without free parameters.
    Returns:
        Gates: Structured as a tuple of (name_gate,applied_qubits,parameters).
        For instance an Rxx gate could look like ("rxx",((0,1),),0.3).
        Connectivity:
    """
    # We start by creating the list of circuit instructions
    # We need to check that the instructions are supported and that the parameters are bound.
    # At the same time we will also keep track of the connectivity in the circuit.
    # Any 2 qubit gate will be added to the connectivity, and to avoid counting duplicates
    # we will take the convention that the pairs are (a,b) with a<b.
    assert len(qc.parameters) == 0, "There are some unbound parameters in the circuit."
    circuit = []
    connectivity = set()
    for inst in qc:
        gate_name = inst.name
        qubit_indices = [q._index+1 for q in inst.qubits]
        parameters = inst.params
        circuit.append((gate_name, tuple(qubit_indices), tuple(parameters)))
        if len(qubit_indices) == 2:
            qubit_indices.sort()
            connectivity.add(tuple(qubit_indices))
        elif len(qubit_indices) > 2 and gate_name != "pauli":
            raise NotImplementedError(
                f"Error with gate:{gate_name}. Gates with more than 3 qubits have not been implemented yet"
            )
    return tuple(circuit), tuple(connectivity)


def observable_description(
    op: SparsePauliOp,
) -> tuple[tuple[str, tuple[int, ...], float], ...]:
    """
    Creates a necessary description of an observable to be used in TensorNetworkQuantumSimulator.
    """
    return tuple(
        (name, tuple(qubits), float(coeff.real))
        for name, qubits, coeff in op.to_sparse_list()
    )
