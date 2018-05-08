#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2018, AVOXI, Inc.
#

"""Setup script
"""

import os

from setuptools import setup

setup(
    name="swaggerpy3",
    version="0.3.0",
    license="BSD 3-Clause License",
    description="Library for accessing Swagger-enabled API's",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.rst")).read(),
    author="AVOXI, Inc.",
    author_email="darren.sessions@avoxi.com",
    url="https://github.com/AVOXI/swaggerpy3",
    packages=["swaggerpy3"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    tests_require=["nose", "tissue", "coverage", "httpretty"],
    install_requires=["aiohttp"],
    entry_points="""
    [console_scripts]
    swagger-codegen = swaggerpy3.codegen:main
    """
)
