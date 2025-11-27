import unittest

from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import GenericBackendV2

from itensornetworks_qiskit.graph import cmap_from_circuit


# TODO: Check what are the topologies that should be mapped and are not.
# Known issues:
# 6 qubit circular connectivity
# Any 1d lattice
class TestCmapFromCircuit(unittest.TestCase):
    pass
