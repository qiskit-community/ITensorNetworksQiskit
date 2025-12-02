from juliacall import Main as jl

jl.seval(
    """using Pkg; 
         Pkg.add(url="https://github.com/JoeyT1994/TensorNetworkQuantumSimulator.git", rev="788acb8293a95797f66a5d5ec226176389920824");
         Pkg.develop(path="./")
    """
)
