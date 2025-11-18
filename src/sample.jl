using TensorNetworkQuantumSimulator
const TNQS = TensorNetworkQuantumSimulator
"""
You cannot call keyword arguments directly in Juliacall, which means we have to have this wrapper
function
# Arguments
- `ψt`: An ITensorNetwork`
- `nsamples`: Number of shots to sample
- `projected_message_rank`: Passed to BoundaryMPSCache, see https://github.com/JoeyT1994/TensorNetworkQuantumSimulator/blob/4f3107286302b913f2ff57d7bd5f350c11518f7b/src/sample.jl#L22
- `norm_message_rank`: Passed to BoundaryMPSCache, see https://github.com/JoeyT1994/TensorNetworkQuantumSimulator/blob/4f3107286302b913f2ff57d7bd5f350c11518f7b/src/sample.jl#L31
"""
function sample_psi(ψt, nsamples, projected_mps_bond_dimension=maxvirtualdim(ψt)*5, norm_mps_bond_dimension=maxvirtualdim(ψt)^2, partition_by="Column")
     nsamples = Int(nsamples)
  return TNQS.sample(network(ψt), nsamples; projected_mps_bond_dimension=projected_mps_bond_dimension,
                norm_mps_bond_dimension=norm_mps_bond_dimension, partition_by=partition_by)
end
