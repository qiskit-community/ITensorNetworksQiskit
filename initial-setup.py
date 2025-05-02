from juliacall import Main as jl;

jl.seval(
    """using Pkg; 
         Pkg.add("ITensorNetworks");
         Pkg.add(url="https://github.com/JoeyT1994/TensorNetworkQuantumSimulator.git", rev="010a27f");
         Pkg.develop(path="./")"""
)
