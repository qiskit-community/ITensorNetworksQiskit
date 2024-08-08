module ITensorNetworksQiskit


include("utils.jl")
export build_graph_from_gates

include("circuitMPS.jl")
export circuit_mps
export mps_from_circuit
export generate_siteindices
export overlap_with_zero
export sigmaz_expectation
export two_site_rdm
export sq_overlap

# heavy hex circuit example 
# heavy hex graph generated at runtime
include("circuitHeavyHex.jl")
export heavy_hex_example
export generate_graph
export tn_from_circuit
export sigmaz_expectation_2d
export get_first_edge_rdm_2d

# simple circuit example
# uses efficient iTensors MPS implementation
# circuit passed in as prop
include("circuitMPSITensors.jl")
export itensors_mps_example
export mps_from_circuit_itensors
export generate_siteindices_itensors
export overlap_with_zero_itensors
export overlap_itensors
export sigmaz_expectation_itensors
export mps_from_circuit_and_mps_itensors

end  # module ITensorNetworksQiskit
