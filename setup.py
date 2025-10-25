#!/usr/bin/env python3
"""
Setup configuration for hacknotts25-pipeline.
This file ensures numpy is not imported at metadata-time.
"""

from setuptools import setup

# No imports of numpy or other heavy dependencies at module level
# All dependencies are declared in pyproject.toml

if __name__ == "__main__":
    setup()
