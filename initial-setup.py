from juliacall import Main as jl;

jl.seval(
    """using Pkg; 
         Pkg.add("ITensorNetworks");
         # Pkg.add(url="https://github.com/JoeyT1994/TensorNetworkQuantumSimulator.git", rev="509309c48c775058cdf6ff5354e470fd66f3776c");
         Pkg.develop(path="./")
         Pkg.develop(path="../TensorNetworkQuantumSimulator")"""
)
