.. role:: python(code)
    :language: python


horast
======

.. image:: https://img.shields.io/pypi/v/horast.svg
    :target: https://pypi.python.org/pypi/horast
    :alt: package version from PyPI

.. image:: https://travis-ci.org/mbdevpl/horast.svg?branch=master
    :target: https://travis-ci.org/mbdevpl/horast
    :alt: build status from Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/mbdevpl/horast?svg=true
    :target: https://ci.appveyor.com/project/mbdevpl/horast
    :alt: build status from AppVeyor

.. image:: https://api.codacy.com/project/badge/Grade/33195093bb1b448bb9a5368b3507d615
    :target: https://www.codacy.com/app/mbdevpl/horast
    :alt: grade from Codacy

.. image:: https://codecov.io/gh/mbdevpl/horast/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mbdevpl/horast
    :alt: test coverage from Codecov

.. image:: https://img.shields.io/pypi/l/horast.svg
    :target: https://github.com/mbdevpl/horast/blob/master/NOTICE
    :alt: license

Attempt at a human-oriented abstract syntax tree (AST) parser/unparser for Python 3.

This package provides new AST node types which inherit from nodes in typed_ast.ast3 module.
Additionally, it provides implementation of parser and unparser for the extended ASTs.

Simple example of how to use this package:

.. code:: python

    from horast import parse, unparse

    tree = parse("""a = 1  # a equals one after this""")
    print(unparse())
    # this will print the code with original comment

More examples in `<examples.ipynb>`_.

technical details
-----------------

Parser is based on built-in tokenize module and typed_ast.ast3.parse() function.

Unparser is essentially an extension of Unparser class from typed_astunparse package.

Nodes provided and handled by horast are listed below.


Comment
~~~~~~~

Full line as well as end-of-line comments are parsed/unparsed correctly when they are outside
of multi-line expressions.

Currently, handling of comments within multi-line expressions is implemented only partially.


Docstring
~~~~~~~~~

To do.


requirements
------------

CPython >= 3.4.

Python libraries as specified in `<requirements.txt>`_.

Building and running tests additionally requires packages listed in `<test_requirements.txt>`_.
