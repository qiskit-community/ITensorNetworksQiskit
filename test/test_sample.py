import unittest
from juliacall import Main as jl
from qiskit.quantum_info import Statevector

from itensornetworks_qiskit.convert import circuit_description
from itensornetworks_qiskit.graph import graph_from_edges, graph_to_grid
from qiskit import QuantumCircuit
from ddt import ddt, data

jl.seval("using ITensorNetworksQiskit")
jl.seval("using TensorNetworkQuantumSimulator")


def sample_from_1d_circuit(qc: QuantumCircuit):
    circuit, edges = circuit_description(qc)
    # Since the qubits are not connected by 2 qubit gates
    # we need to define the edges manually
    qubit_map = graph_to_grid(graph_from_edges(edges), 3)
    bpc, error = jl.tn_from_circuit(circuit, qubit_map, edges, 5, 1e-12)
    print(bpc)
    jl_samples = jl.sample_psi(bpc, 10, 5, 5, partition_by="column")
    jl_samples_translated = jl.translate_samples(jl_samples, qubit_map)
    samples = jl.pydict(jl_samples_translated)
    return samples


@ddt
class TestSample(unittest.TestCase):
    @data([0, 1, 2, 3, 4])
    def test_ordering_samples(self, qubit_flips: list[int]):
        """
        We test that the ordering of the qubits is correct.
        We will flip some qubits so that all the samples are
        the same bitstring.
        """
        qc = QuantumCircuit(5)
        for q in range(qc.num_qubits - 1):
            qc.rxx(0.3, q, q + 1)
        for q in qubit_flips:
            qc.x(q)
        tn_samples = sample_from_1d_circuit(qc)
        target_samples = Statevector(qc).sample_counts(10)
        self.assertEqual(tn_samples, target_samples)
