from juliacall import Main as jl

jl.seval(
    """using Pkg; 
         Pkg.add("ITensorNetworks");
         Pkg.add(url="https://github.com/JoeyT1994/TensorNetworkQuantumSimulator.git", rev="69fa7546f6c06216879b73fcd4f62c80bd08cb8a");
         Pkg.develop(path="./")"""
)
