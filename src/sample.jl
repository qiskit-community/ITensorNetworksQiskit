using TensorNetworkQuantumSimulator
const TNQS = TensorNetworkQuantumSimulator
"""
Wrapper function for TNQS.sample. This is needed as keyword arguments cannot be used directly in
    Juliacall. For more details on the bond dimenions see https://arxiv.org/abs/2507.11424.
# Arguments
- `ψ_bpc`: A BeliefPropagationCache 
- `nsamples`: Number of shots to sample
- `projected_mps_bond_dimension`:  Bond dimension of the projected boundary MPS messages used during contraction of the projected state <x|ψ>.
- `norm_mps_bond_dimension`: Bond dimension of the boundary MPS messages used to contract <ψ|ψ>.
- `partition_by`: "column" or "row": how to partition the graph.

"""
function sample_psi(
    ψ_bpc,
    nsamples,
    projected_mps_bond_dimension = maxvirtualdim(ψ_bpc) * 5,
    norm_mps_bond_dimension = maxvirtualdim(ψ_bpc)^2,
    alg = "boundarymps",
    partition_by = "column",
)
    nsamples = Int(nsamples)
    ψ = network(ψ_bpc)
    return TNQS.sample(
        ψ,
        nsamples;
        alg = alg,
        projected_mps_bond_dimension = projected_mps_bond_dimension,
        norm_mps_bond_dimension = norm_mps_bond_dimension,
        partition_by = partition_by,
    )
end
