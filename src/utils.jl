# Many of the functions here are adapted or copied from
# https://github.com/JoeyT1994/ITensorNetworksExamples so that we have a stable versioned copy here

function build_bp_cache(ψ::AbstractITensorNetwork; kwargs...)
  bpc = BeliefPropagationCache(QuadraticFormNetwork(ψ))
  bpc = update(bpc; kwargs...)
  return bpc
end

function ITensors.apply(
    o::ITensor,
    ψ::AbstractITensorNetwork,
    bpc::BeliefPropagationCache;
    reset_all_messages=false,
    apply_kwargs...,
    )
    bpc = copy(bpc)
    ψ = copy(ψ)
    vs = neighbor_vertices(ψ, o)
    envs = incoming_messages(bpc, PartitionVertex.(vs))
    singular_values! = Ref(ITensor())
    ψ = noprime(apply(o, ψ; envs, singular_values!, apply_kwargs...))
    ψdag = prime(dag(ψ))
    if length(vs) == 2
    v1, v2 = vs
    pe = partitionedge(bpc, (v1, "bra") => (v2, "bra"))
    mts = messages(bpc)
    ind2 = commonind(singular_values![], ψ[v1])
    δuv = dag(copy(singular_values![]))
    δuv = replaceind(δuv, ind2, ind2')
    map_diag!(sign, δuv, δuv)
    singular_values![] = denseblocks(singular_values![]) * denseblocks(δuv)
    if !reset_all_messages
      set!(mts, pe, dag.(ITensor[singular_values![]]))
      set!(mts, reverse(pe), ITensor[singular_values![]])
    else
      bpc = BeliefPropagationCache(partitioned_tensornetwork(bpc))
    end
    end
    for v in vs
    bpc = update_factor(bpc, (v, "ket"), ψ[v])
    bpc = update_factor(bpc, (v, "bra"), ψdag[v])
    end
    return ψ, bpc
end

function gate_to_itensor(gate, s::IndsNetwork)
    op_string = first(gate)
    inds = reduce(vcat, s[v] for v in gate[2])
    length(gate) == 3 && return op(op_string, inds; last(gate)...)
    length(gate) == 2 && return op(op_string, inds)
end

function sq_overlap(ψ::ITensorNetwork, ϕ::ITensorNetwork; normalized = false, alg = "bp")
    numerator = inner(ψ, ϕ; alg)
    numerator = numerator * conj(numerator)
    denominator = !normalized ? inner(ψ, ψ; alg) * inner(ϕ, ϕ; alg) : 1.0
    return real(numerator / denominator)
end

#Note that region should consist of contiguous vertices here!
function rdm(ψ::ITensorNetwork, region; (cache!)=nothing, cache_update_kwargs=(;))
    cache = isnothing(cache!) ? build_bp_cache(ψ; cache_update_kwargs...) : cache![]
    ψIψ = tensornetwork(cache)

    state_tensors = vcat(
    ITensor[ψIψ[ket_vertex(ψIψ, v)] for v in region],
    ITensor[ψIψ[bra_vertex(ψIψ, v)] for v in region],
    )
    env = incoming_messages(cache, PartitionVertex.(region))

    rdm = contract(ITensor[env; state_tensors]; sequence="automatic")

    s = siteinds(ψ)
    rdm = permute(
    rdm, vcat(reduce(vcat, [s[v] for v in region]), reduce(vcat, [s[v]' for v in region]))
    )

    rdm = array((rdm * combiner(inds(rdm; plev=0)...)) * combiner(inds(rdm; plev=1)...))
    rdm /= tr(rdm)

    return rdm
end

function heavy_hex_lattice_graph(n::Int64, m::Int64)
    """Create heavy-hex lattice geometry"""
    g = named_hexagonal_lattice_graph(n, m)
    g = decorate_graph_edges(g)

    vertex_rename = Dictionary()
    for (i, v) in enumerate(vertices(g))
        set!(vertex_rename, v, (i,))
    end
    g = rename_vertices(v -> vertex_rename[v], g)

    return g
end

function ITensors.op(
    ::OpName"xx_plus_yy",
    ::SiteType"S=1/2";
    θ::Float64 = pi / 2,
    β::Float64 = 0.0,
)
    mat = zeros(ComplexF64, 4, 4)
    mat[1, 1] = 1
    mat[4, 4] = 1
    mat[2, 2] = cos(0.5 * θ)
    mat[2, 3] = -1.0 * im * sin(0.5 * θ) * exp(-1.0 * im * β)
    mat[3, 2] = -1.0 * im * sin(0.5 * θ) * exp(1.0 * im * β)
    mat[3, 3] = cos(0.5 * θ)
    return mat
end

#Construct a graph with edges everywhere a two-site gate appears.
function build_graph_from_gates(gate_list)
    vertices = []
    edges = []
    for gate in gate_list
        gate_verts = gate[2]
        if length(gate_verts) == 1
            if only(gate_verts) ∉ vertices
                push!(vertices, only(gate_verts))
            end
        elseif length(gate_verts) == 2
            vsrc, vdst = gate_verts[1], gate_verts[2]
            if vsrc ∉ vertices
                push!(vertices, vsrc)
            end
            if vdst ∉ vertices
                push!(vertices, vdst)
            end
            e = NamedEdge(vsrc => vdst)
            if e ∉ edges || reverse(e) ∉ edges
                push!(edges, e)
            end
        end
    end
    g = NamedGraph()
    g = add_vertices(g, vertices)
    g = add_edges(g, edges)
    return g
end

function filter_zero_terms(H::OpSum)
    H_out = OpSum()
    for h in H
        if !iszero(first(h.args))
            H_out += h
        end
    end
    return H_out
end
