import numpy as np
from juliacall import Main as jl

jl.seval("using QiskitTNQS")
jl.seval("using TensorNetworkQuantumSimulator")

def rdm(psi, verts, alg="bp"):
    """
    A python wrapper for reduced_density_matrix in TensorNetworkQuantumSimulator with conversion
    with a numpy array after.
    """
    itn_rdm = jl.reduced_density_matrix(psi, verts, alg=alg)
    np_rdm = np.array(jl.itensor_to_density_matrix(itn_rdm, bra_positions=[1, 4], ket_positions=[2, 3])).reshape((4, 4))
    return np_rdm