# qiskit-tnqs

**qiskit-tnqs** is a lightweight library that enables simulation of Qiskit circuits using
[TensorNetworkQuantumSimulator.jl](https://github.com/JoeyT1994/TensorNetworkQuantumSimulator.jl). 
There are a number of end-to-end examples for using this code in the `examples` folder.

> [!WARNING]
> This library is an interface to [TensorNetworkQuantumSimulator.jl](https://github.com/JoeyT1994/TensorNetworkQuantumSimulator.jl) which uses belief propagation
> for the underlying simulation. Beyond the error introduced by normal tensor network approximations
> (e.g., finite bond dimension), the belief propagation ansatz is only fully accurate for a tree graph.
> If the graph of the circuit is not a tree, then belief propagation is only an approximation
> and all results should be taken with caution as they are approximate. The severity of this 
> approximation can vary drastically and extensive testing should be done to validate it. 
> See https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.5.010308 and https://arxiv.org/abs/2507.11424 for examples
> where extensive testing is done to quantify the accuracy of the BP approximation for a 
> a loopy tensor network.

## Installation and Setup

Once you have cloned the repository, you should be able to get started using the following steps:

 1. start your python env
 2. `pip install .`
 3. `python initial-setup.py`
 4. `python examples/run_heavy_hex.py` (similarly for other examples)

## Contribution Guidelines

If you'd like to contribute, please take a look at the
[contribution guidelines](CONTRIBUTING.md).
This project adheres to Qiskit's 
[code of conduct](https://github.com/Qiskit/qiskit/blob/master/CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.

## Authors and Citation

`qiskit-tnqs` was originally authored by 
[Kate Marshall](mailto:kate.marshall@ibm.com), [Lewis Anderson](mailto:lewis.anderson@ibm.com), 
[Ben Jaderberg](mailto:benjamin.jaderberg@ibm.com) and
[Joey Tindall](mailto:jtindall@flatironinstitute.org). 

If you use this codebase for your research, please cite the latest version and extended author list
from Zenodo:
https://doi.org/10.5281/zenodo.16926968.

## License

This project uses the [Apache License 2.0](LICENSE). Like any other Apache 2 licensed code, you are free to use it or/and extend it.


