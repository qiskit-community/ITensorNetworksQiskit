using ITensorNetworks
const ITN = ITensorNetworks

# Adapted from main() in
# https://github.com/JoeyT1994/ITensorNetworksExamples/examples/circuitHeavyHex.jl

"""
    tn_from_circuit(gates, chi, s, nlayers, bp_update_freq)

Returns an ITensorNetwork corresponding to the action of the gates on the |00..0> state. See the
/examples/ directory for examples of usage.

# Arguments
- `gates`: Gates in the format returned by `qiskit_circ_to_itn_circ_2d()`
- `chi`: Maximum bond dimension for the simulatin
- `s`: Site indices as built from ITensorNetworks.siteinds
- `nlayers`: The number of times to repeat the entire circuit. The belief propagation cache will
be updated after each layer, which is a good strategy for Trotter circuits.
- `bp_update_freq`: Defines after how many gates the belief propagation cache should be updated.
Setting to 0 (default) will not update the cache here, meaning it is only updated through defining
`nlayers`. Setting to 1 will update the cache after every gate and give the lowest error from the
BP approximation.
"""
function tn_from_circuit(gates, chi, s, nlayers, bp_update_freq=0)
    if startswith(gates, "[")
        gates = eval(Meta.parse(gates))
    end
    ψ = ITensorNetwork(v -> "↑", s)
    maxdim, cutoff = chi, 1e-14
    apply_kwargs = (; maxdim, cutoff, normalize = true)
    #Parameters for BP, as the graph is not a tree (it has loops), we need to specify these
    set_global_bp_update_kwargs!(;
        maxiter = 30,
        tol = 1e-10,
        message_update_kwargs = (;
            message_update_function = ms -> make_eigs_real.(ITN.default_message_update(ms))
        ),
    )
    bpc = build_bp_cache(ψ)
    ψ, bpc = apply(gates, ψ, bpc; apply_kwargs, verbose = false)
    max_chi = maxlinkdim(ψ)
    println("Final chi: $max_chi")


    return ψ, bpc
end

function generate_graph(nx, ny)
    g = heavy_hex_lattice_graph(nx, ny)
    nqubits = length(vertices(g))
    return g, nqubits
end

function sigmaz_expectation_2d(ψ, sites, bpc)
    sites_tuples = [(n,) for n in sites]
    expect_sigmaz = real.(expect(ψ, "Z", sites_tuples; (cache!)=Ref(bpc)))
end

## TODO: generalise this to pass in a tuple of a pair which is known to be in the graph
function get_first_edge_rdm_2d(ψ, bpc, g)
     first_edge = first(edges(g))
     println("First edge is $first_edge")
     site1, site2 = src(first_edge), dst(first_edge)
     ρ = rdm(ψ, [site1, site2]; (cache!) = Ref(bpc))
     return ρ
end
