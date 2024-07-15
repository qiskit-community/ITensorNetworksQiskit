using NamedGraphs.NamedGraphGenerators: named_grid
using ITensors: Trotter, siteinds, expect
using ITensorNetworks: ITensorNetwork, update, maxlinkdim
using ITensorNetworks.ModelHamiltonians: heisenberg

include("utils.jl")

function main()

    nx, ny = 2, 2
    #Build a qubit layout of 2x2 heavy hexagons
    g = heavy_hex_lattice_graph(nx, ny)
    nqubits = length(vertices(g))
    s = siteinds("S=1/2", g; conserve_qns = true)
    ψ = ITensorNetwork(v -> isodd(first(v)) ? "↑" : "↓", s)
    maxdim, cutoff = 10, 1e-14
    apply_kwargs = (; maxdim, cutoff)
    #Parameters for BP, as the graph is not a tree (it has loops), we need to specify these
    bp_update_kwargs = (; maxiter = 25, tol = 1e-8)
    bpc = build_bp_cache(ψ; bp_update_kwargs...)
    h, J = 0.5, -1.0
    no_trotter_steps = 10
    δt = 1e-2

    #Specifying the circuit, here we do CX on each neighbouring pair of qubits followed by Rn on all qubits
    H = filter_zero_terms(heisenberg(g))
    U = exp(-im * δt * H, alg = Trotter{2}())
    gates = Vector{ITensor}(U, s)

    χinit = maxlinkdim(ψ)
    println("Initial bond dimension of the state is $χinit")

    initial_mag = sum(real.(expect(ψ, "Z"; alg = "bp"))) / nqubits
    println("Initial Mag is $initial_mag")
    time = 0

    for i = 1:no_trotter_steps
        println("Time is $time")
        for gate in gates
            ψ, bpc = apply(gate, ψ, bpc; apply_kwargs...)
        end
        #Update the BP cache after each trotter step here. Should be frequent enough is delta_t << 1
        bpc = update(bpc; bp_update_kwargs...)
        time += δt
    end

    χfinal = maxlinkdim(ψ)
    println("Final bond dimension of the state is $χfinal")

    final_mag = sum(real.(expect(ψ, "Z"; alg = "bp"))) /nqubits
    println("Final Mag is $final_mag")
end

main()
