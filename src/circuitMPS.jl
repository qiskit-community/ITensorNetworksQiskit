using NamedGraphs.NamedGraphGenerators: named_grid
using ITensors: siteinds, expect
using ITensorNetworks: ITensorNetwork, update

include("utils.jl")

function mps_from_circuit(L, gates, chi, s)
    if startswith(gates, "[")
        gates = eval(Meta.parse(gates))
    end
    #Initialise the tensor network, all qubits down (in Z basis)
    ψ = ITensorNetwork(v -> "↑", s)
    #Maximum bond dimension and the SVD cutoff to use
    maxdim, cutoff = chi, 1e-14
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

function mps_from_circuit(L, gates, chi)
    s = generate_siteindices(L)
    return mps_from_circuit(L, gates, chi, s)
end

function mps_from_circuit(L, gates)
    return mps_from_circuit(L, gates, 10)
end

function generate_siteindices(L)
    #Build the graph that reflects our tensor network
    g = named_grid((L, 1))
    s = siteinds("S=1/2", g)
    return s
end

function overlap_with_zero(ψ, s)
    ψref = ITensorNetwork(v -> "↑", s)
    f = sq_overlap(ψ, ψref)
    return f
end


function sigmaz_expectation(ψ, sites)
    sites_tuples = [(n, 1) for n in sites]
    expect_sigmaz = real.(expect(ψ, "Z", sites_tuples))
end

function two_site_rdm(ψ, bpc, site1, site2)
     ρ = two_site_rdm(ψ, (site1, 1), (site2, 1), (cache!) = Ref(bpc))
     return ρ
end
