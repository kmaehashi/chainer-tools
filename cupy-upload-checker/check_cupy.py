#!/usr/bin/env python

import os
import sys

import distlib.locators


wheel_projects = [
    'cupy-cuda90',
    'cupy-cuda92',
    'cupy-cuda100',
    'cupy-cuda101',
    'cupy-cuda102',
    'cupy-cuda110',
    'cupy-cuda111',
]

wheel_projects_legacy = [
    'cupy-cuda90',
    'cupy-cuda92',
    'cupy-cuda100',
    'cupy-cuda101',
    'cupy-cuda102',
    'cupy-cuda110',
    'cupy-cuda111',
]

wheel_archs = [
    'cp35-cp35m-manylinux1_x86_64',
    'cp36-cp36m-manylinux1_x86_64',
    'cp37-cp37m-manylinux1_x86_64',
    'cp38-cp38-manylinux1_x86_64',

    'cp36-cp36m-win_amd64',
    'cp37-cp37m-win_amd64',
    'cp38-cp38-win_amd64',
]


wheel_archs_legacy = wheel_archs


def get_basenames(project, version):
    locator = distlib.locators.PyPIJSONLocator('https://pypi.org/pypi')
    proj = locator.get_project(project)
    if version not in proj:
        return []
    return [os.path.basename(url) for url in proj[version].download_urls]

def get_expected_sdist_basename(project, version):
    return '{project}-{version}.tar.gz'.format(
        project=project,
        version=version,
    )

def get_expected_wheel_basename(project, version, arch):
    return '{project}-{version}-{arch}.whl'.format(
        project=project.replace('-', '_'),
        version=version,
        arch=arch,
    )

def verify(project, expected, actual):
    print('# Project: {}'.format(project))
    expected = set(expected)
    actual = set(actual)
    error = False
    for project in (expected - actual):
        error = True
        print('missing: {}'.format(project))
    for project in (actual - expected):
        error = True
        print('unexpected: {}'.format(project))
    if not error:
        print('OK')
    print()

def main(argv):
    version = argv[1]
    legacy = int(version[0]) < 9

    # sdist
    project = 'cupy'
    expected = [get_expected_sdist_basename(project, version)]
    actual = get_basenames(project, version)
    verify(project, expected, actual)

    # wheel
    for project in (wheel_projects_legacy if legacy else wheel_projects):
        expected = [
            get_expected_wheel_basename(project, version, arch)
            for arch in (wheel_archs_legacy if legacy else wheel_archs)
        ]
        actual = get_basenames(project, version)
        verify(project, expected, actual)

if __name__ == '__main__':
    main(sys.argv)
