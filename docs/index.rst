.. stmdency documentation master file, created by
   sphinx-quickstart on Sat Dec  3 23:11:01 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stmdency's Documentation
========================

Stmdency, **ST** ate **M** ents depen **DENCY**, a tool handling python statements' dependencies, can
extract dependencies from python statements according to the given statement identifier.

Installation
------------

Stmdency can be installed from PyPI using pip:

.. code-block:: bash

   python -m pip install stmdency

Usage
-----

Stmdency can be used as a python module(as a command line tool will comming soon).

.. code-block:: python

   from stmdency.extractor import Extractor

   statement = """
   a = 1
   b = a + 2
   """
   extractor = Extractor(source=statement)
   print(extractor.get_code("b"))
   # a = 1
   #
   # b = a + 2

or for function name:

.. code-block:: python

   from stmdency.extractor import Extractor

   statement = """
   a = 1
   b = 2
   def bar():
       b = a + 3
       print(a, b)
   def foo():
       bar(b)
   """
   extractor = Extractor(source=statement)
   print(extractor.get_code("foo"))
   # a = 1
   #
   # b = 2
   #
   # def bar():
   #     b = a + 3
   #     print(a, b)
   #
   # def foo():
   #     bar(b)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
