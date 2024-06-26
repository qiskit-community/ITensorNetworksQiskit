from juliacall import Main as jl; 
jl.seval(
    """using Pkg; 
         Pkg.add("NamedGraphs"); 
         Pkg.add("ITensors"); 
         Pkg.add("ITensorNetworks"); 
         Pkg.add("Graphs"); 
         Pkg.add("DataGraphs");
         Pkg.add("Glob"); 
         Pkg.add("Dictionaries"); 
         Pkg.add("SplitApplyCombine");
         Pkg.develop(path="./")"""
)
