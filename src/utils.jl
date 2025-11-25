# Some of the functions here are adapted or copied from
# https://github.com/JoeyT1994/ITensorNetworksExamples so that we have a stable versioned copy here

function overlap_with_zero(ψ::BeliefPropagationCache)
  ψ_0= tensornetworkstate(ComplexF32, v -> "↑" ,ψ.network.tensornetwork.graph, "S=1/2")
  #TODO: We can implement this function once we figure out how.
  #For now this is a way of createing the 0 state.
end
