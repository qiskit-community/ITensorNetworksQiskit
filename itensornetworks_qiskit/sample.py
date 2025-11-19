import re
from collections import Counter


# def parse_samples(shots):
#     """
#     Parse a JuliaCall object like
#       Dictionaries.Dictionary{Tuple{Int64, Int64}, Int64}[{(1, 1) = 1, (2, 1) = 1, ...}, {…}, …]
#     into a Python list of dicts [{(1,1):1, …}, {…}, …] via the string representation.
#     # TODO Can we find a way to directly convert this using JuliaCall without strings and regex?
#     """
#     # Create a string of entire Julia obj e.g., "Dictionaries.Dictionary{Tuple{...."
#     shots_str = str(shots)
#     # Separate each shot into its own string by capturing all characters between and incl { and }
#     dict_strs = re.findall(r'\{[^}]*}', shots_str)
#
#     # The Julia type gets caught by our regex above, remove it
#     if "Tuple" in dict_strs[0]:
#         del dict_strs[0]
#
#     # For each shot, pull out all "(qnx, qny) = b" pairs where (q1x, q1y) are the 2d coordinates
#     # on the heavy hex for qubit n and b is a single bit value 0 or 1.
#     out = []
#     for ds in dict_strs:
#         body = ds[1:-1]  # strip the outer {…}
#         # In each shot we have the form "(qnx, qny) = b". First we look for a "(" character and
#         # capture the digit qnx. Then after a comma and possible whitespace we capture qny. We then
#         # look for ")" to know vertices are ended. Finally, after "=" and possible whitespaces
#         # we capture the final digit which is the bit value 0 or 1.
#         pairs = re.findall(r'\(*(\d+)*,\s*(\d+)*\)\s*=\s*(\d+)', body)
#         d = {(int(i), int(j)): int(v) for i, j, v in pairs}
#         out.append(d)
#
#     return out
#

# def sample_dict_to_bitstring(sample_dict, qmap_inv):
#     """
#     Converts a single shot, passed as dictionary of 2d qubit coordinate to bit value, to
#     a bitstring e.g., 10110...
#     :param sample_dict: Of the form {(1, 1): 0, (1, 2): 1, ... }
#     :param qmap_inv: A mapping from 2d coordinate (i, j) to Qiskit qubit index in
#     """
#     bits = ["0"] * len(sample_dict)
#     for qubit_coord, bit in sample_dict.items():
#         if bit:
#             bits[qmap_inv[qubit_coord] - 1] = "1"
#     return ("".join(reversed(bits)))


def itn_samples_to_counts_dict(, qmap: dict):
    """
    Converts samples returned by TensorNetworkQuantumSimulator.sample to the Qiskit format
    :param shots: Of type juliacall.VectorValue in the form
    Dictionaries.Dictionary{Tuple{Int64, Int64}, Int64}
    :param qmap: Mapping from qubit index to 2d coordinate on heavy-hex, likely previously passed
    to `qiskit_circ_to_itn_circ_2d()`.
    :return: dict of {bitstring: count} where bitstring uses Qiskit's little endian notation
    qn...q2q1q0
    """

    samples_qiskit = []
    for sample in samples:
        samples_qiskit.append(([jl.get(sample, coord, None) for _, coord in qubit_map]))
    print(samples_qiskit)

    return samples_qiskit

     
    # # Get a list of shots, where each shot is a dictionary of vertex to bit value
    # py_shots = parse_samples(shots)
    # # Define a mapping from qubit coords
    # qmap_inv = {v: k for k, v in qmap.items()}
    # bitstrings = [sample_dict_to_bitstring(shot, qmap_inv) for shot in py_shots]
    # accumulated_shots = dict(Counter(bitstrings))
    # return accumulated_shots
