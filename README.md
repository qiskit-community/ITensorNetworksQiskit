**Running the code**
1. Assuming you have Julia installed: from within the repo call `julia --project` to access julia with the environment set to match the environment specified by this repo.
2. The first time you run the code call
```
using Pkg
Pkg.instantiate()
```
in order to download and initialise the projects dependencies (including the specified versions). These are detailed in the file `project.toml`

**The BP Cache**
1. The `bp_cache` object stores information about the environments associated with the norm `<psi|psi>` of a tensor network `psi`. This information is necessary to perform o
  operations on `psi` such as: i) applying a gate, ii) taking an expectation value, iii) forming an rdm. Details about how belief propagation works on a tensor network can
  can be found in: https://www.scipost.org/SciPostPhys.15.6.222?acad_field_slug=chemistry
2. The `bp_cache` cache needs to be updated every time the network `psi` changes in order to be up to date. However, we can sometimes get away with less frequent changes
if the underlying network undergoes only small changes (say becuase we did Trotterised time evolution applied gates which are fairly close to the identity matrix). It is up
to the user to make sure the cache is updated frequently enough that the results are accurate.
3. If the underlying graph `g` is a tree (no loops) then the cache will (assuming it is up to date) accurately contain the environments in the network and any operation
performed will be accurate up to the error incurred by any truncation. This is the case in the `circuitMPS.jl` code. If the graph `g` is not a tree then the `bp_cache` is only an approximation and all results
should be taken with caution as they are approximate. The severity of this approximation can vary drastically and extensive testing should be done to validate it. 
See https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.5.010308 for an example paper where extensive testing is done to verify the accuracy of the BP approximation
for the example of a loopy network.







