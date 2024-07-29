using NamedGraphs.NamedGraphGenerators: named_grid
using ITensors: siteinds, expect
using ITensors.ITensorMPS: sample, MPS, orthogonalize!

include("utils.jl")

function itensors_mps_example()

    L = 4
    #Build the graph that reflects our tensor network
    s = siteinds("S=1/2", L)
    #Initialise the tensor network, all qubits down (in Z basis)
    ψ = MPS(s, [isodd(n) ? "Dn" : "Up" for n in 1:L])
    ψref = MPS(s, [isodd(n) ? "Dn" : "Up" for n in 1:L])


    #Maximum bond dimension and the SVD cutoff to use
    maxdim, cutoff = 10, 1e-14
    apply_kwargs = (; maxdim, cutoff)

    #Specifying the circuit, each gates is [string, vertices to act on, optional_params]
    gates = [
        ("X", 1),                        # Pauli X on qubit 1
        ("CX", 1,2),                   # Controlled-X on qubits [1,2]
        ("Rx", 2, (θ = 0.5,)),              # Rotation of θ around X
        ("Rn", 3, (θ = 0.5, ϕ = 0.2, λ = 1.2)), # Arbitrary rotation with angles (θ,ϕ,λ)
        ("√SWAP", 3,4),                # Sqrt Swap on qubits [3,4]
        ("T", 4),
    ]

    no_layers = 3

    expect_sigmaz = real.(expect(ψ, "Z"; sites = [1,3]))
    println("Initial Sigma Z on selected sites is $expect_sigmaz")

    samples = [sample(orthogonalize!(ψ,1)) for i in 1:2]
    println("Two samples from ψ are $(first(samples)) and $(last(samples))")

    #Run the circuit
    for i = 1:no_layers
        println("Running circuit layer $i")
        for gate in gates
            o = op(gate, s)
            ψ = apply(o, ψ; apply_kwargs...)
        end

    end

    expect_sigmaz = real.(expect(ψ, "Z"; sites = [1,3]))
    println("Final Sigma Z on selected sites is $expect_sigmaz")

    f =  inner(ψ, ψref) / sqrt(inner(ψ,ψ)*inner(ψref,ψref))
    println("Overlap with initial state $(f*conj(f))")

    samples = [sample(orthogonalize!(ψ,1)) for i in 1:2]
    println("Two samples from ψ are $(first(samples)) and $(last(samples))")
end

function mps_from_circuit_itensors(L, gates, maxdim, cutoff, s)
    if startswith(gates, "[")
        gates = eval(Meta.parse(gates))
    end

    ψ = MPS(s, ["Up" for n in 1:L])
    apply_kwargs = (; maxdim, cutoff)
    for gate in gates
        o = op(gate, s)
        ψ = apply(o, ψ; apply_kwargs...)
    end

    return ψ
end

function mps_from_circuit_itensors(L, gates, chi, s)
   return mps_from_circuit_itensors(L, gates, chi, 1e-14, s)
end

function mps_from_circuit_and_mps_itensors(ψ, gates, maxdim, cutoff, s)
    if startswith(gates, "[")
        gates = eval(Meta.parse(gates))
    end

    apply_kwargs = (; maxdim, cutoff)
    for gate in gates
        o = op(gate, s)
        ψ = apply(o, ψ; apply_kwargs...)
    end

    return ψ
end

function generate_siteindices_itensors(L)
    s = siteinds("S=1/2", L)
    return s
end

function overlap_with_zero_itensors(L, ψ, s)
    ψref = MPS(s, ["Up" for n in 1:L])
    f =  overlap_itensors(ψ, ψref)
    return f
end

function overlap_itensors(ψ1, ψ2)
    numerator = inner(ψ1, ψ2)
    numerator = numerator * conj(numerator)
    return real(numerator / sqrt(inner(ψ1,ψ1)*inner(ψ2,ψ2)))
end

function sigmaz_expectation_itensors(ψ, sites)
    expect_sigmaz = real.(expect(ψ, "Z"; sites = sites))
end
