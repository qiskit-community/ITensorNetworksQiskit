using TensorNetworkQuantumSimulator
const TNQS = TensorNetworkQuantumSimulator
"""
You cannot call keyword arguments directly in Juliacall, which means we have to have this wrapper
function
# Arguments
- `ψ_bpc`: A BeliefPropagationCache 
- `nsamples`: Number of shots to sample
- `projected_message_rank`: Passed to BoundaryMPSCache, see https://github.com/JoeyT1994/TensorNetworkQuantumSimulator/blob/4f3107286302b913f2ff57d7bd5f350c11518f7b/src/sample.jl#L22
- `norm_message_rank`: Passed to BoundaryMPSCache, see https://github.com/JoeyT1994/TensorNetworkQuantumSimulator/blob/4f3107286302b913f2ff57d7bd5f350c11518f7b/src/sample.jl#L31
"""
function sample_psi(ψ_bpc, nsamples, projected_mps_bond_dimension=maxvirtualdim(ψt)*5, norm_mps_bond_dimension=maxvirtualdim(ψt)^2, partition_by="column")
     nsamples = Int(nsamples)
     ψ = network(ψ_bpc)
  return TNQS.sample(ψ, nsamples; alg = "boundarymps", projected_mps_bond_dimension=projected_mps_bond_dimension,
                norm_mps_bond_dimension=norm_mps_bond_dimension, partition_by=partition_by)
end


