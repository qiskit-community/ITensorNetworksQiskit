using NamedGraphs.NamedGraphGenerators: named_grid
using ITensors: siteinds, expect
using ITensorNetworks: ITensorNetwork, update, maxlinkdim

include("utils.jl")

function heavy_hex_example()
    nx, ny = 2, 3
    #Build a qubit layout of 2x3 heavy hexagons (49 qubits)
    g = heavy_hex_lattice_graph(nx, ny)
    nqubits = length(vertices(g))
    s = siteinds("S=1/2", g)
    ψ = ITensorNetwork(v -> "↑", s)
    ψref = ITensorNetwork(v -> "↓", s)
    maxdim, cutoff = 10, 1e-14
    apply_kwargs = (; maxdim, cutoff)
    #Parameters for BP, as the graph is not a tree (it has loops), we need to specify these
    bp_update_kwargs = (; maxiter = 25, tol = 1e-8)
    bpc = build_bp_cache(ψ; bp_update_kwargs...)

    #Specifying the circuit, here we do CX on each neighbouring pair of qubits followed by Rn on all qubits
    two_site_gates = [("CX", [src(e), dst(e)]) for e in edges(g)]
    single_site_gates = [("Rn", [v], (θ = 0.5, ϕ = 0.2, λ = 1.2)) for v in vertices(g)]
    gates = vcat(two_site_gates, single_site_gates)
    # println("Gates to append to circuit are $gates")

    no_layers = 3
    #Edge (pair of neighboring qubits) to take the rdm for
    e_rdm = first(edges(g))
    #Vertices to measure "Z" on
    vs_measure = [(1,), (nqubits,)]

    χinit = maxlinkdim(ψ)
    println("Initial bond dimension of the state is $χinit")

    expect_sigmaz = real.(expect(ψ, "Z", vs_measure))
    println("Initial Sigma Z on selected sites is $expect_sigmaz")

    f = sq_overlap(ψ, ψref)
    println("Initial Overlap with all spins down is $f")

    ρ = two_site_rdm(ψ, src(e_rdm), dst(e_rdm); (cache!) = Ref(bpc))
    println("Initial RDM on selected sites is $ρ")

    for i = 1:no_layers
        println("Running circuit layer $i")
        for gate in gates
            o = gate_to_itensor(gate, s)
            ψ, bpc = apply(o, ψ, bpc; reset_all_messages = false, apply_kwargs...)
        end
        #Update the BP cache after each layer here. Should be good until we start making truncations.
        bpc = update(bpc; bp_update_kwargs...)
    end

    χfinal = maxlinkdim(ψ)
    println("Final bond dimension of the state is $χfinal")

    expect_sigmaz = real.(expect(ψ, "Z", vs_measure))
    println("Initial Sigma Z on selected sites is $expect_sigmaz")

    f = sq_overlap(ψ, ψref)
    println("Final Overlap with all spins down is $f")

    ρ = two_site_rdm(ψ, src(e_rdm), dst(e_rdm), (cache!) = Ref(bpc))
    println("Final RDM on selected sites is $ρ")
end

function tn_from_circuit(gates, chi, s, nlayers)
    if startswith(gates, "[")
        gates = eval(Meta.parse(gates))
    end
    ψ = ITensorNetwork(v -> "↑", s)
    maxdim, cutoff = chi, 1e-14
    apply_kwargs = (; maxdim, cutoff)
    #Parameters for BP, as the graph is not a tree (it has loops), we need to specify these
    bp_update_kwargs = (; maxiter = 25, tol = 1e-8)
    bpc = build_bp_cache(ψ; bp_update_kwargs...)

    for i = 1:nlayers
        println("Running circuit layer $i")
        for gate in gates
            o = gate_to_itensor(gate, s)
            ψ, bpc = apply(o, ψ, bpc; reset_all_messages = false, apply_kwargs...)
        end
        #Update the BP cache after each layer here. Should be good until we start making truncations.
        bpc = update(bpc; bp_update_kwargs...)
        max_chi = maxlinkdim(ψ)
        println("Final chi: $max_chi")
    end


    return ψ, bpc
end

function generate_graph(nx, ny)
    g = heavy_hex_lattice_graph(nx, ny)
    nqubits = length(vertices(g))
    return g, nqubits
end

function sigmaz_expectation_2d(ψ, sites)
    sites_tuples = [(n,) for n in sites]
    expect_sigmaz = real.(expect(ψ, "Z", sites_tuples))
end

#TODO generalise this to pass in a tuple of a pair which is known to be in the graph
function get_first_edge_rdm_2d(ψ, bpc, g)
     first_edge = first(edges(g))
     println("First edge is $first_edge")
     site1, site2 = src(first_edge), dst(first_edge)
     ρ = two_site_rdm(ψ, site1, site2, (cache!) = Ref(bpc))
     return ρ
end
