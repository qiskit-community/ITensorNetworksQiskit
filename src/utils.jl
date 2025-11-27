# Some of the functions here are adapted or copied from
# https://github.com/JoeyT1994/ITensorNetworksExamples so that we have a stable versioned copy here
using ITensors

function overlap_with_zero(ψ::BeliefPropagationCache)
    ψ_0 = tensornetworkstate(ComplexF32, v -> "↑", ψ.network.tensornetwork.graph, "S=1/2")
    #TODO: We can implement this function once we figure out how.
    #For now this is a way of createing the 0 state.
end


# function flatten_density_matrix(ρ::ITensor)
#   indices=inds(ρ)
#   ρ_flat= jl.Array(itn_rdm, *indices)
#   return ρ_flat
# end

using ITensors

"""
    itensor_to_density_matrix(T::ITensor; bra_positions=nothing, ket_positions=nothing)

Convert an ITensor representing a k-qubit density matrix into a Julia `Matrix` of size (2^k, 2^k).

Arguments:
- `T`: ITensor with 2k indices (bra and ket).
- `bra_positions`: positions of bra indices.
- `ket_positions`: positions of ket indices.

Returns:
- `rho`: Dense Julia Matrix of size (2^k, 2^k).
"""
function itensor_to_density_matrix(T::ITensor; bra_positions, ket_positions)
    inds_T = inds(T)
    n = length(inds_T) / 2  # number of qubits

    # Reorder indices: bra first, then ket
    ordered_inds = vcat(inds_T[bra_positions], inds_T[ket_positions])

    # Convert to dense Julia Array with correct order
    return Array(T, ordered_inds...)
end
