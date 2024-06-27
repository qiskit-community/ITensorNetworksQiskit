using NamedGraphs.NamedGraphGenerators: named_grid
using ITensors: siteinds, expect
using ITensorNetworks: ITensorNetwork, update

include("utils.jl")

function circuitMPS(L, gates)

    if startswith(gates, "[")
        gates = eval(Meta.parse(gates))
    end

    #Build the graph that reflects our tensor network
    g = named_grid((L, 1))
    s = siteinds("S=1/2", g)
    #Initialise the tensor network, all qubits down (in Z basis)
    ψ = ITensorNetwork(v -> "↑", s)
    #Reference state for overlap
    ψref = ITensorNetwork(v -> "↓", s)
    #Maximum bond dimension and the SVD cutoff to use
    maxdim, cutoff = 10, 1e-14
    apply_kwargs = (; maxdim, cutoff)
    #Parameters for BP, as the graph is a tree (no loops), BP will automatically set the right parameters
    bp_update_kwargs = (;)
    bpc = build_bp_cache(ψ; bp_update_kwargs...)

    #Specifying the circuit, each gates is [string, vertices to act on, optional_params]
    # gates = [
    #     ("X", [(1, 1)]),                        # Pauli X on qubit 1
    #     ("CX", [(1, 1), (2, 1)]),                   # Controlled-X on qubits [1,2]
    #     ("Rx", [(2, 1)], (θ = 0.5,)),              # Rotation of θ around X
    #     ("Rn", [(3, 1)], (θ = 0.5, ϕ = 0.2, λ = 1.2)), # Arbitrary rotation with angles (θ,ϕ,λ)
    #     ("√SWAP", [(3, 1), (4, 1)]),                # Sqrt Swap on qubits [3,4]
    #     ("T", [(4, 1)]),
    # ]

    expect_sigmaz = real.(expect(ψ, "Z", [(1, 1), (3, 1)]))
    println("Initial Sigma Z on selected sites is $expect_sigmaz")

    f = sq_overlap(ψ, ψref)
    println("Initial Overlap with all spins down is $f")

    ρ = two_site_rdm(ψ, (1, 1), (2, 1); (cache!) = Ref(bpc))
    println("Initial RDM on selected sites is $ρ")

    #Run the circuit
    for gate in gates
        o = gate_to_itensor(gate, s)
        ψ, bpc = apply(o, ψ, bpc; apply_kwargs...)
        #Update the BP cache after each gate here.
        bpc = update(bpc; bp_update_kwargs...)
    end

    expect_sigmaz = real.(expect(ψ, "Z", [(1, 1), (3, 1)]))
    println("Initial Sigma Z on selected sites is $expect_sigmaz")

    f = sq_overlap(ψ, ψref)
    println("Final Overlap with all spins down is $f")

    ρ = two_site_rdm(ψ, (1, 1), (2, 1), (cache!) = Ref(bpc))
    println("Final RDM on selected sites is $ρ")
    return ρ
end
