using NamedGraphs.NamedGraphGenerators: named_grid
using ITensors: siteinds, expect
using ITensors.ITensorMPS: sample, MPS, orthogonalize!

include("utils.jl")

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
