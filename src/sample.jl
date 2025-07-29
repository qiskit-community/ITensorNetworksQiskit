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
function sample_psi(ψt, nsamples, projected_message_rank=maxlinkdim(ψt)*5, norm_message_rank=maxlinkdim(ψt)^2, partition_by="Column")
     return TNQS.sample(ψt, nsamples; projected_message_rank=projected_message_rank,
                norm_message_rank=norm_message_rank, partition_by=partition_by)
end
