from juliacall import Main as jl;

jl.seval(
    """using Pkg; 
         Pkg.add("ITensorNetworks");
         Pkg.add(url="https://github.com/JoeyT1994/TensorNetworkQuantumSimulator.git", rev="d68550f197fd05d5d39bc8003dfebae63cc38f6f");
         Pkg.develop(path="./")"""
)
