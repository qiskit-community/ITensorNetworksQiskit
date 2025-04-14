from juliacall import Main as jl; 
jl.seval(
    """using Pkg; 
         Pkg.add("ITensorNetworks"); 
         Pkg.develop(path="./")"""
)
