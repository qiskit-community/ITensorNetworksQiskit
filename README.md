# ITensorNetworksQiskit

**ITensorNetworks Qiskit** is a set of tools that have been built to enable easy use of [ITensorNetworks.jl](https://github.com/ITensor/ITensorNetworks.jl) 
 for tensor network simulations of quantum circuits build in Qiskit. This repository was originally 
contributed to by [Joey Tindall](mailto:jtindall@flatironinstitute.org), who has kindly shared various examples of 
building ITensorNetworks representations of quantum circuits for simulation experiments. Our 
contribution on top of this is additional functionality to make this code usable from Qiskit. We have
provided a number of end-to-end examples for using this code in the `examples` folder.

For context, the structure of this repository has been guided by the needs for setting up a Julia package.
The role of each folder is as below:
 
 - `src`: is where the Julia code, including building tensor network representations of quantum circuits 
 using ITensorNetworks. 
 - `test`: is where test material will live. This is currently just a placeholder, as the existing test 
 material exists in `examples` folder with end-to-end example material. This `test` folder will be populated
 with unit test material in due course.
 - `itensornetworks_qiskit`: is where various Python-based utility functions live that assist in translating
 between Qiskit and ITensorNetworks or ITensor, enabling the examples found in `examples`
 - `examples`: is where you will find end-to-end examples of Qiskit code calling Julia ITensorNetworks and 
 ITensor using the `juliacall` Python package.
 - Files find in the root of the repository are all concerned with installation and setup, for which you will
 find full instructions below.

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

`ITensorNetworksQiskit` was inspired, authored and brought about by the collective work of 
[Kate Marshall](mailto:kate.marshall@ibm.com), [Lewis Anderson](mailto:lewis.anderson@ibm.com) and 
[Ben Jaderberg](mailto:benjamin.jaderberg@ibm.com) working closely with 
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


