#!/usr/bin/env python

import os
import sys

import distlib.locators


project = sys.argv[1]
version = sys.argv[2]

locator = distlib.locators.PyPIRPCLocator('https://pypi.org/pypi')
for url in locator.get_project(project)['urls'][version]:
    print(os.path.basename(url))
