import unittest
import matplotlib.pyplot as plt
from qiskit.circuit.library import real_amplitudes
from juliacall import Main as jl
from qiskit.quantum_info import Statevector

from itensornetworks_qiskit.convert import circuit_description
from itensornetworks_qiskit.graph import graph_from_edges, graph_to_grid
from rustworkx.visualization import mpl_draw
from qiskit import QuantumCircuit
from ddt import ddt, data

jl.seval("using ITensorNetworksQiskit")
jl.seval("using TensorNetworkQuantumSimulator")


def sample_from_circuit(qc: QuantumCircuit):
    circuit, edges = circuit_description(qc)
    # Since the qubits are not connected by 2 qubit gates
    # we need to define the edges manually
    g = graph_from_edges(edges)
    qubit_map = graph_to_grid(g, 6)
    bpc, error = jl.tn_from_circuit(circuit, qubit_map, edges, 5, 1e-12)
    print(bpc)
    jl_samples = jl.sample_psi(bpc, 10)
    jl_samples_translated = jl.translate_samples(jl_samples, qubit_map)
    samples = jl.pydict(jl_samples_translated)
    return samples


@ddt
class TestSample(unittest.TestCase):
    @data([0, 1, 2, 3, 4], [0, 3, 5], [0], [7], [3, 6])
    def test_ordering_samples(self, qubit_flips: list[int]):
        """
        We test that the ordering of the qubits is correct.
        We will flip some qubits so that all the samples are
        the same bitstring.
        """
        # qc = real_amplitudes(8, entanglement="circular")
        # qc.assign_parameters([0.0] * qc.num_parameters, inplace=True)
        qc = QuantumCircuit(8)
        # TODO: For now all the qubits need to be connected by at least 1 gate in order to be part of the graph.
        # Ideally we would like to include those qubits in the graph as well in order to allow for idle qubits.
        for q in range(qc.num_qubits):
            qc.cx(q, (q + 1) % qc.num_qubits)
        for q in qubit_flips:
            qc.x(q)
        tn_samples = sample_from_circuit(qc)
        target_samples = Statevector(qc).sample_counts(10)
        print(tn_samples)
        print(target_samples)
        self.assertEqual(tn_samples, target_samples)
