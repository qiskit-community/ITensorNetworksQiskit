from juliacall import Main as jl

jl.seval(
    """using Pkg; 
         Pkg.add("ITensorNetworks");
         Pkg.add(url="https://github.com/JoeyT1994/TensorNetworkQuantumSimulator.git", rev="e0b17e0d8a3ed43435b9e7b75aff68d76e2aec9c");
         Pkg.develop(path="./")"""
)
