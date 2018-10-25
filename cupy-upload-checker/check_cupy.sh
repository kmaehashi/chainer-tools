#!/bin/sh -ue

VERSION="${1}"
for PKG in cupy cupy-cuda80 cupy-cuda90 cupy-cuda91 cupy-cuda92; do
    echo "${PKG}: "
    ./show_package_names.py "${PKG}" "${VERSION}" | sort
    echo
done
