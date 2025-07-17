using ITensorNetworks
const ITN = ITensorNetworks

# Adapted from main() in
# https://github.com/JoeyT1994/ITensorNetworksExamples/examples/circuitHeavyHex.jl

"""
    tn_from_circuit(gates, chi, s, nlayers, bp_update_freq)

Returns an ITensorNetwork corresponding to the action of the gates on the |00..0> state. See the
/examples/ directory for examples of usage.

Belief propagation uses the default convergence settings defined in
https://github.com/JoeyT1994/TensorNetworkQuantumSimulator/blob/main/src/Backend/beliefpropagation.jl.
Furthermore, the belief propagation cache is updated every time an overlapping gate is encountered
(i.e., every time the two-qubit circuit depth increases), the default behaviour in
TensorNetworkQuantumSimulator.

# Arguments
- `gates`: Gates in the format returned by `qiskit_circ_to_itn_circ_2d()`
- `chi`: Maximum bond dimension for the simulatin
- `s`: Site indices as built from ITensorNetworks.siteinds
"""
function tn_from_circuit(gates, chi, s)
    if startswith(gates, "[")
        gates = eval(Meta.parse(gates))
    end
    ψ = ITensorNetwork(v -> "↑", s)
    apply_kwargs = (; cutoff = 1e-12, maxdim = chi)

    bpc = build_bp_cache(ψ)
    ψ, bpc, errors = apply(gates, ψ, bpc; apply_kwargs)
    println("Max bond dimension: $(maxlinkdim(ψ))")
    println("Maximum gate error for layer was $(maximum(errors))")
    return ψ, bpc
end

function generate_graph(nx, ny)
    g = heavy_hex_lattice_graph(nx, ny)
    nqubits = length(vertices(g))
    return g, nqubits
end

function overlap_with_zero(ψ, s)
    ψref = ITensorNetwork(v -> "↑", s)
    f = sq_overlap(ψ, ψref)
    return f
end

function pauli_expectation(pauli, ψ, sites, bpc)
     """
    Calculates the expectation value of a 1-body pauli observable "X", "Y", or "Z" for each
    site in sites. Uses the default expectation algorithm, which is belief propagation.
    """
    observables = [(pauli, [n]) for n in sites]
    expect_sigmaz = real.(expect(ψ, observables; (cache!)=Ref(bpc)))
end

function pauli_expectation_boundarymps(pauli, ψ, sites, boundarymps_rank)
    """
    Similar to pauli_expectation above, uses the boundary MPS method, which is more precise and
    slower. See https://github.com/JoeyT1994/TensorNetworkQuantumSimulator/blob/22f8017e9798974bfe62f57afbc64ff9e239c246/src/expect.jl#L98
    for more details.
    """
    observables = [(pauli, [n]) for n in sites]
    expect_sigmaz = real.(expect(ψ, observables; alg="boundarymps", cache_construction_kwargs = (; message_rank = boundarymps_rank)))
end

## TODO: generalise this to pass in a tuple of a pair which is known to be in the graph
function get_first_edge_rdm_2d(ψ, bpc, g)
     first_edge = first(edges(g))
     site1, site2 = src(first_edge), dst(first_edge)
     ρ = rdm(ψ, [site1, site2]; (cache!) = Ref(bpc))
     return ρ
end
