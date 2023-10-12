# Stmdency

[![PyPi Version](https://img.shields.io/pypi/v/stmdency.svg?style=flat-square&logo=PyPi)](https://pypi.org/project/stmdency/)
[![PyPi Python Versions](https://img.shields.io/pypi/pyversions/stmdency.svg?style=flat-square&logo=python)](https://pypi.org/project/stmdency/)
[![PyPi License](https://img.shields.io/:license-Apache%202-blue.svg?style=flat-square)](https://raw.githubusercontent.com/zhongjiajie/stmdency/main/LICENSE)
[![PyPi Status](https://img.shields.io/pypi/status/stmdency.svg?style=flat-square)](https://pypi.org/project/stmdency/)
[![Downloads](https://pepy.tech/badge/stmdency/month)](https://pepy.tech/project/stmdency)
[![Coverage Status](https://img.shields.io/codecov/c/github/zhongjiajie/stmdency/main.svg?style=flat-square)](https://codecov.io/github/zhongjiajie/stmdency?branch=main)  <!-- markdown-link-check-disable-line -->
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat-square&labelColor=ef8336)](https://pycqa.github.io/isort)
[![CI](https://github.com/zhongjiajie/stmdency/actions/workflows/ci.yaml/badge.svg)](https://github.com/zhongjiajie/stmdency/actions/workflows/ci.yaml)
[![Documentation Status](https://readthedocs.org/projects/stmdency/badge/?version=latest)](https://stmdency.readthedocs.io/en/latest/?badge=latest)

stmdency, **sta**tement depen**dency** is a Python library for extracting dependencies between statements in a Python program.

## Installation

```shell
python -m pip install --upgrade stmdency
```

## Usage

Let's say we have a Python script named  `test.py` with the following content:

```python
a = 1
b = 2

def bar():
   b = a + 3
   print(a, b)

def foo():
   bar(b)
```

We want to extract function `foo` and all its dependencies. `stmdency` can do this for us:

```python
from stmdency.extractor import Extractor

with open("test.py", "r") as f:
   source = f.read()
   extractor = Extractor(source)
   print(extractor.get_code("foo"))
```

The output will be:

```python
a = 1

def bar():
    b = a + 3
    print(a, b)

b = 2

def foo():
    bar(b)
```

## Documentation

The documentation host read the doc and is available at [https://stmdency.readthedocs.io](https://stmdency.readthedocs.io).

## Who is using stmdency?

- [dolphinscheduler-sdk-python](https://github.com/apache/dolphinscheduler-sdk-python): Python API to manage Dolphinscheduler workflow by code, aka PyDolphinscheduler.
