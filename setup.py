# See pyproject.toml for project configuration.
# This file exists for compatibility with legacy tools:
# https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html

from setuptools import setup, find_packages
import subprocess

setup(
    name="ITensorNetworksQiskit",
    version="0.0",
    description="ITensorNetworksQiskit",
    author="Lewis Anderson, Kate Marshall, Ben Jaderberg",
    author_email="lewis.anderson@ibm.com, kate.marshall@ibm.com, benjamin.jaderberg@ibm.com",
    license="MIT",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "qiskit~=1.0.2",
        "juliacall",
    ],
)
