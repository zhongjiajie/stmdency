.. stmdency documentation master file, created by
   sphinx-quickstart on Sat Dec  3 23:11:01 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stmdency
========

Stmdency, **ST** ate **M** ents depen **DENCY**, a tool handling python statements' dependencies, can
extract dependencies from Python statements according to the given statement identifier.

Installation
============

Stmdency can be installed from PyPI using pip:

.. code-block:: bash

   python -m pip install --upgrade stmdency


Usage
=====

Stmdency can be used as a Python module(as a command line tool will coming soon).

Extract Variable Dependencies
-----------------------------

Let's say we have a python code like below, we define a variable ``a`` and ``b`` and ``b`` depends on ``a``:

.. code-block:: python

   a = 1
   b = a + 2

Now we want to extract variable ``b`` and all of its dependencies, and we want to make sure our extracted code
can be executed. Stmdency can help us to do this:

.. code-block:: python

   from stmdency.extractor import Extractor

   statement = """
   a = 1
   b = a + 2
   """

   extractor = Extractor(source=statement)
   result = extractor.get_code("b")
   print(result)

The result will be:

.. code-block:: python

   a = 1

   b = a + 2


Extract Function Dependencies
-----------------------------

Stmdency not only can extract variable dependencies, but also can extract function dependencies. Suppose we
have the script below.

.. code-block:: python

   a = 1
   b = 2

   def bar():
       b = a + 3
       print(a, b)

   def foo():
       bar(b)

Now we want to extract function ``foo`` and all of its dependencies, and we want to make our extracted code
runnable.

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
   
The result will be:

.. code-block:: python

   a = 1
   
   b = 2
   
   def bar():
       b = a + 3
       print(a, b)
   
   def foo():
       bar(b)

Python Code in File
-------------------

As you can see, we use a string to represent the Python code in the above examples. But in most cases, our code
is in a file. Stmdency can also handle this situation.

First, we need to create a file named ``test.py`` and write the code below into it:

.. code-block:: bash

   cat <<EOF > test.py
   a = 1
   b = 2
   
   def bar():
       b = a + 3
       print(a, b)
   
   def foo():
       bar(b)
   EOF

Then we can use the code below to extract function ``foo`` and all of its dependencies:

.. code-block:: python

   from stmdency.extractor import Extractor
   
   with open("test.py", "r") as f:
       source = f.read()
       extractor = Extractor(source)
       print(extractor.get_code("foo"))

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
