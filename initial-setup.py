from juliacall import Main as jl

jl.seval(
    """using Pkg; 
         Pkg.add("ITensorNetworks");
         Pkg.add(url="https://github.com/JoeyT1994/TensorNetworkQuantumSimulator.git");
         Pkg.develop(path="./")"""
)
