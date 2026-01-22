
import unittest
import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp
from juliacall import Main as jl

from qiskit_tnqs.convert import circuit_description, observable_description, SUPPORTED_GATES
from qiskit_tnqs.graph import graph_from_edges, graph_to_grid

jl.seval("using QiskitTNQS")
jl.seval("using TensorNetworkQuantumSimulator")


class TestCircuits(unittest.TestCase):
    def simulate(self, qc, chi=4, cutoff=1e-12):
        circuit, edges = circuit_description(qc)
        qmap = graph_to_grid(graph_from_edges(edges))
        psi, _ = jl.tn_from_circuit(circuit, qmap, edges, chi, cutoff)
        return jl.rescale(psi), qmap

    def expect_tnqs(self, psi, qmap, obs):
        obs_jl = jl.translate_observable(observable_description(obs), qmap)
        val = jl.expect(psi, obs_jl)
        return float(np.asarray(val).reshape(-1)[0].real)

    def test_supported_gate_circuits(self):
        for gate in sorted(SUPPORTED_GATES):
            with self.subTest(gate=gate):
                qc = QuantumCircuit(2)
                qc.h(0)
                qc.cx(0, 1)

                if gate == "rx":
                    qc.rx(0.7, 0)
                elif gate == "ry":
                    qc.ry(-1.2, 1)
                elif gate == "rz":
                    qc.rz(0.4, 0)
                elif gate == "rxx":
                    qc.rxx(0.9, 0, 1)
                elif gate == "ryy":
                    qc.ryy(-0.8, 0, 1)
                elif gate == "rzz":
                    qc.rzz(0.6, 0, 1)
                elif gate == "cx":
                    qc.cx(1, 0)
                elif gate == "h":
                    qc.h(1)
                elif gate == "x":
                    qc.x(0)
                elif gate == "y":
                    qc.y(1)
                elif gate == "z":
                    qc.z(0)

                qc.cx(0, 1)

                psi, qmap = self.simulate(qc)
                sv = Statevector(qc)

                tnqs_psi = jl.network(psi)
                zero = jl.zerostate(tnqs_psi.tensornetwork.graph, tnqs_psi.siteinds)
                tnqs_overlap = float(abs(jl.inner(zero, tnqs_psi, alg="bp")) ** 2)
                qiskit_overlap = float(abs(sv[0]) ** 2)
                self.assertAlmostEqual(tnqs_overlap, qiskit_overlap, places=10)

                for qubit in (0, 1):
                    for pauli in ("X", "Z"):
                        with self.subTest(qubit=qubit, pauli=pauli):
                            obs = SparsePauliOp.from_sparse_list([(pauli, [qubit], 1.0)], 2)
                            tnqs_val = self.expect_tnqs(psi, qmap, obs)
                            qiskit_val = float(np.real(sv.expectation_value(obs)))
                            self.assertAlmostEqual(tnqs_val, qiskit_val, places=9)


class TestTwoQubitRotations(unittest.TestCase):
    def simulate(self, qc, chi=32, cutoff=1e-12):
        circuit, edges = circuit_description(qc)
        qmap = graph_to_grid(graph_from_edges(edges))
        psi, _ = jl.tn_from_circuit(circuit, qmap, edges, chi, cutoff)
        return jl.rescale(psi), qmap

    def expect(self, psi, qmap, spo):
        obs_jl = jl.translate_observable(observable_description(spo), qmap)
        v = jl.expect(psi, obs_jl)
        return float(np.asarray(v).reshape(-1)[0].real)

    def prob00(self, psi):
        net = jl.network(psi)
        zero = jl.zerostate(net.tensornetwork.graph, net.siteinds)
        return float(abs(jl.inner(zero, net, alg="bp")) ** 2)

    def test_rxx_angle_respected(self):
        for theta in (0.2, 0.6, -1.1):
            with self.subTest(theta=theta):
                qc = QuantumCircuit(2)
                qc.rxx(theta, 0, 1)
                psi, _ = self.simulate(qc)
                sv = Statevector(qc)
                self.assertAlmostEqual(self.prob00(psi), float(abs(sv[0]) ** 2), places=10)

    def test_ryy_angle_respected(self):
        for theta in (0.2, 0.6, -1.1):
            with self.subTest(theta=theta):
                qc = QuantumCircuit(2)
                qc.ryy(theta, 0, 1)
                psi, _ = self.simulate(qc)
                sv = Statevector(qc)
                self.assertAlmostEqual(self.prob00(psi), float(abs(sv[0]) ** 2), places=10)

    def test_rzz_angle_respected(self):
        for theta in (0.2, 0.6, -1.1):
            with self.subTest(theta=theta):
                qc = QuantumCircuit(2)
                qc.h(0); qc.h(1)
                qc.rzz(theta, 0, 1)
                psi, qmap = self.simulate(qc)
                sv = Statevector(qc)
                tnqs_xx = self.expect(psi, qmap, SparsePauliOp("XX"))
                qiskit_xx = float(np.real(sv.expectation_value(SparsePauliOp("XX"))))
                self.assertAlmostEqual(tnqs_xx, qiskit_xx, places=9)


if __name__ == "__main__":
    unittest.main()
