#!/usr/bin/env python
# -*- coding: utf-8 -*- #

"""
pysitemaps: A Python Package for website sitemap Files.

MIT License
Copyright (c) 2022 SERP Wings www.serpwings.com
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = "0.0.3"

setup(
    name="pysitemaps",
    version=version,
    author="Faisal Shahzad",
    author_email="seowingsorg@gmail.com",
    description="Python Package for Sitemaps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/serpwings/pysitemaps/",
    project_urls={
        "Bug Tracker": "https://github.com/serpwings/pysitemaps/issues",
        "Documentation": "https://pysitemaps.pages.dev/",
    },
    classifiers=[
        "Topic :: Utilities",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Education",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries",
    ],
    packages=["pysitemaps"],
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "dev": [
            "setuptools",
            "pytest",
            "pytest-cov",
            "twine",
            "wheel",
            "mkdocs",
            "mkdocs-gen-files",
            "mkdocstrings[python]",
            "pymdown-extensions",
        ]
    },
)
