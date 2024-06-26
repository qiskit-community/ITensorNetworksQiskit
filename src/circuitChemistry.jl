using NamedGraphs.NamedGraphGenerators: named_grid
using ITensors: siteinds, expect
using ITensorNetworks: ITensorNetwork, update, maxlinkdim

include("utils.jl")

function main()

    maxdim, cutoff = 10, 1e-14
    apply_kwargs = (; maxdim, cutoff)
    #Parameters for BP, as the graph is not a tree (it has loops), we need to specify these
    bp_update_kwargs = (; maxiter = 25, tol = 1e-8)

    #Specifying the circuit, here we do CX on each neighbouring pair of qubits followed by Rn on all qubits
    gates = [
        ("xx_plus_yy", [(1,), (2,)], (; θ = 0.5, β = 0.1)),
        ("X", [(1,)]),
        ("P", [(3,)], (; ϕ = 0.4)),
        ("CPHASE", [(3,), (5,)], (; ϕ = 0.4)),
        ("xx_plus_yy", [(1,), (3,)], (; θ = 0.5, β = 0.1)),
    ]

    g = build_graph_from_gates(gates)
    nqubits = length(vertices(g))
    s = siteinds("S=1/2", g)
    ψ = ITensorNetwork(v -> "↑", s)
    ψref = ITensorNetwork(v -> "↓", s)
    bpc = build_bp_cache(ψ; bp_update_kwargs...)

    no_layers = 1
    #Edge (pair of neighboring qubits) to take the rdm for
    e_rdm = first(edges(g))
    #Vertices to measure "Z" on
    vs_measure = [(1,), (3,)]

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

main()
