# See pyproject.toml for project configuration.
# This file exists for compatibility with legacy tools:
# https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html

from setuptools import setup, find_packages

setup(
    name="ITensorNetworksQiskit",
    version="0.0",
    description="ITensorNetworksQiskit",
    author="Kate Marshall, Lewis Anderson, Ben Jaderberg, Joey Tindall",
    author_email="kate.marshall@ibm.com, lewis.anderson@ibm.com, benjamin.jaderberg@ibm.com, jtindall@flatironinstitute.org",
    license="Apache V2",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "qiskit>=1.3,~2.1.1",
        "juliacall",
        "matplotlib~=3.9.0",
        "pylatexenc~=2.10",
        "networkx~=3.4.2",
        "qiskit-ibm-runtime~=0.40.1"
    ],
)
