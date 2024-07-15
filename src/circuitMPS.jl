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
    println("Final Sigma Z on selected sites is $expect_sigmaz")

    f = sq_overlap(ψ, ψref)
    println("Final Overlap with all spins down is $f")

    ρ = two_site_rdm(ψ, (1, 1), (2, 1), (cache!) = Ref(bpc))
    println("Final RDM on selected sites is $ρ")

end

function mps_from_circuit(L, gates)
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

    #Run the circuit
    for gate in gates
        o = gate_to_itensor(gate, s)
        ψ, bpc = apply(o, ψ, bpc; apply_kwargs...)
        #Update the BP cache after each gate here.
        bpc = update(bpc; bp_update_kwargs...)
    end

    return ψ, bpc
end

function overlap_with_zero_from_circ(L, gates)
    # Can't seem to get this to work when inputting a ψ instead of entire circuit
    # juliacall.JuliaError: AssertionError: issetequal(flatten_siteinds(bra), flatten_siteinds(ket))
    if startswith(gates, "[")
        gates = eval(Meta.parse(gates))
    end

    g = named_grid((L, 1))
    s = siteinds("S=1/2", g)
    ψ = ITensorNetwork(v -> "↑", s)
    ψref = ITensorNetwork(v -> "↑", s)
    maxdim, cutoff = 10, 1e-14
    apply_kwargs = (; maxdim, cutoff)
    bp_update_kwargs = (;)
    bpc = build_bp_cache(ψ; bp_update_kwargs...)

    for gate in gates
        o = gate_to_itensor(gate, s)
        ψ, bpc = apply(o, ψ, bpc; apply_kwargs...)
        bpc = update(bpc; bp_update_kwargs...)
    end

    f = sq_overlap(ψ, ψref)
    return f
end

function sigmaz_expectation(ψ, sites)
    sites_tuples = [(n, 1) for n in sites]
    expect_sigmaz = real.(expect(ψ, "Z", sites_tuples))
end

function two_site_rdm_from_circuit(ψ, bpc, site1, site2)
     ρ = two_site_rdm(ψ, (site1, 1), (site2, 1), (cache!) = Ref(bpc))
     return ρ
end
