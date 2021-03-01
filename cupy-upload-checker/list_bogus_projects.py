#!/usr/bin/env python

import time
import socket
import sys

from distlib.locators import PyPIRPCLocator


valid_projects = set([
    'cupy',
    'cupy-cuda70',
    'cupy-cuda75',
    'cupy-cuda80',
    'cupy-cuda90',
    'cupy-cuda91',
    'cupy-cuda92',
    'cupy-cuda100',
    'cupy-cuda101',
    'cupy-cuda102',
    'cupy-cuda110',
    'cupy-cuda111',
    'cupy-cuda112',
    'cupy-rocm-4-0',

    # Maintained by external collaborators
    'cupy-ibmopt',
])


# Note: being listed here does NOT represent that the CuPy team acknowledges or supports the project.
known_unrelated_projects = set([
    'accupy',  # Accurate sums and dot products for Python
    'docupy',  # A markdown library.
    'icupy',  # Python bindings for ICU4C
    'molecupy',  # A Python molecular modeller with PDB parsing.
    'ocupy',  # Oculography Analysis Toolbox
    'okcupyd',  # A package for interacting with okcupid.com
    'quantpycupy',  # QuantPy Plugin using CuPy, that extends quantum Executor/Simulator.
    'rescupy',  # RESCUPy is a Python interface for the Fortran-2008 version of RESCU.
])


def _get_distribution_names():
    locator = PyPIRPCLocator('https://pypi.org/pypi')
    for i in range(5):
        try:
            return locator.get_distribution_names()
        except socket.timeout:
            sys.stderr.write('PyPI timed out, retrying...\n')
            time.sleep(3)


def main():
    candidates = set([x for x in _get_distribution_names() if 'cupy' in x])
    for prj in sorted(candidates - valid_projects - known_unrelated_projects):
        print(prj)


if __name__ == '__main__':
    main()
