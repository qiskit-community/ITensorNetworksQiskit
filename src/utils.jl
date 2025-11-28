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

