import unittest

from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import GenericBackendV2

from itensornetworks_qiskit.graph import cmap_from_circuit


class TestCmapFromCircuit(unittest.TestCase):
    def test_given_qc_with_no_qubit_indices_then_valid_edges_still_returned(self):
        qc = QuantumCircuit(4)
        edges = [[0, 1], [0, 2], [0, 3], [1, 3]]
        for edge in edges:
            qc.cx(edge[0], edge[1])
        backend = GenericBackendV2(4, coupling_map=edges)
        qc = transpile(qc, basis_gates=["rx", "ry", "rz", "cx"], backend=backend)
        for gate in qc:
            for qubit in gate.qubits:
                qubit._index = None

        self.assertEqual(sorted(cmap_from_circuit(qc)), edges)
