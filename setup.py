"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="keysightdsox2000",
    version="0.0.1",
    description="Python interface to the Keysight DSO-X 2000 scopes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/quantop-dungeon/KeysightDSOX2000",
    author="QUANTOP",
    author_email="ivan.galinskiy@nbi.ku.dk",
    classifiers=[
        "Development Status :: 3 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="sample, setuptools, development",
    packages=find_packages(where="."),
    python_requires=">=3.6, <4"
)
