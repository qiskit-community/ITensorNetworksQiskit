from juliacall import Main as jl

gates = '[("X", [(1, 1)]), ("CX", [(1, 1), (2, 1)]), ("Rx", [(2, 1)], (θ = 0.5,)), ("Rn", [(3, 1)], (θ = 0.5, ϕ = 0.2, λ = 1.2)), ("√SWAP", [(3, 1), (4, 1)]), ("T", [(4, 1)])]'
jl.seval(
    f"""include("./src/ITensorNetworksQiskit.jl");
    circuitMPS({gates})"""
)
