# ITensorNetworksQiskit

**ITensorNetworksQiskit** is a lightweight library that enables easy use of [ITensorNetworks.jl](https://github.com/ITensor/ITensorNetworks.jl) 
for tensor network simulations of quantum circuits built in Qiskit. There are a number 
of end-to-end examples for using this code in the `examples` folder.

> [!WARNING]
> This library is an interface to [ITensorNetworks.jl](https://github.com/ITensor/ITensorNetworks.jl) which uses belief propagation
> for the underlying simulation. Beyond the error introduced by normal tensor network approximations
> (e.g., finite bond dimension), the belief propagation ansatz is only fully accurate for a tree graph.
> If the graph of the circuit is not a tree, then belief propagation is only an approximation
> and all results should be taken with caution as they are approximate. The severity of this 
> approximation can vary drastically and extensive testing should be done to validate it. 
> See https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.5.010308 for an example paper 
> where extensive testing is done to verify the accuracy of the BP approximation for the example of 
> a loopy network.

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

The structure of this repository as follows:
 
 - `src`: is where the Julia code, including building tensor network representations of quantum circuits 
 using ITensorNetworks. 
 - `test`: is where test material will live. This is currently just a placeholder, as the existing test 
 material exists in `examples` folder with end-to-end example material. This `test` folder will be populated
 with unit test material in due course.
 - `itensornetworks_qiskit`: is where various Python-based utility functions live that assist in translating
 between Qiskit and ITensorNetworks or ITensor, enabling the examples found in `examples`
 - `examples`: is where you will find end-to-end examples of Qiskit code calling Julia ITensorNetworks and 
 ITensor using the `juliacall` Python package.
 - Files found in the root of the repository are all concerned with installation and setup

## Authors and Citation

`ITensorNetworksQiskit` was authored by 
[Kate Marshall](mailto:kate.marshall@ibm.com), [Lewis Anderson](mailto:lewis.anderson@ibm.com), 
[Ben Jaderberg](mailto:benjamin.jaderberg@ibm.com) and
[Joey Tindall](mailto:jtindall@flatironinstitute.org). 

If you use this codebase for your research, please cite using the following BibTeX:

```bibtex
@software{itensornetworks_qiskit,
  author = {{Lewis W. Anderson, Ben Jaderberg, Kate V. Marshall, Joseph Tindall}},
  title = {{ITensorNetworksQiskit: Tools for running ITensorNetworks.jl simulations of Qiskit quantum circuits.}},
  url = {https://github.com/kvcmarshall6/ITensorNetworksQiskit}
}
```

## License

This project uses the [Apache License 2.0](LICENSE). Like any other Apache 2 licensed code, you are free to use it or/and extend it.


