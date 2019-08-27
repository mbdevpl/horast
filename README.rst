.. role:: python(code)
    :language: python


horast
======

Human-oriented abstract syntax tree (AST) parser/unparser for Python 3 that doesn't discard comments.

.. image:: https://img.shields.io/pypi/v/horast.svg
    :target: https://pypi.org/project/horast
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

.. image:: https://img.shields.io/github/license/mbdevpl/horast.svg
    :target: https://github.com/mbdevpl/horast/blob/master/NOTICE
    :alt: license

This package provides new AST node types (Comment and Directive) which inherit from nodes in typed_ast.ast3 module.
Additionally, it provides implementation of parser and unparser for the extended AST allowing
straightforward readable code generation.

Simple example of how to use this package:

.. code:: python

    from horast import parse, unparse

    tree = parse("""a = 1  # a equals one after this""")
    print(unparse(tree))
    # this will print the code with original comment

More examples in `<examples.ipynb>`_.


technical details
-----------------

Parser is based on built-in tokenize module, as well as community packages asttokens and typed_ast.

Unparser is essentially an extension of Unparser class from static_typing package.

Nodes provided and handled by horast are listed below.


Comment
~~~~~~~

Full line as well as end-of-line comments are parsed/unparsed correctly when they are outside
of multi-line expressions.

Currently, handling of comments within multi-line expressions is implemented only partially.


BlockComment
~~~~~~~~~~~~

**Not implemented yet.**

This node type is intended to store consecutive full-line comments in a
single AST node, therefore simplifying handling of large blocks of comments.


Directive
~~~~~~~~~

Since Python doesn't offer a direct way to convey directives in code,
comments beginning with any of the following prefixes will not be classified
as typical comments, but as directives:

*   if
*   else
*   endif
*   def
*   undef
*   ifdef
*   ifndef

However in Python code they still remain as usual comments.

For example, the comments in the following code will all be classified as directives.

.. code:: python

    #ifdef DEBUG
    debugging = True
    #else
    debugging = False
    #fi

However, when executed as Python, ``debugging`` will always end up ``False``
because directives are preserved as usual comments in Python and therefore
they are ignored.

Therefore, the ``Directive`` node is not meant to enable preprocessing of
Python, at least for now.

Note: the prefix is checked exactly. See the following example:

.. code:: python

    #if something
    # if some other thing

The comment in the first line will become ``Directive`` object, while the one
on the second like will become ``Comment`` object.

Currently, this node is meant to work towards AST compatibility between
Python and other languages, to aide code generation from Python AST into code
in other languages -- one such use case is
`*transpyle* project <https://github.com/mbdevpl/transpyle>`_.


Pragma
~~~~~~

``Pragma`` nodes follow the same general rules as ``Directive`` nodes, i.e. they are
stored in Python code as comments, but a comment will be classified as a pragma
when it's prefixed with a predefined prefix:

*   ``" pragma:"``

Additionally, two subclasses of Pragma are defined in horast, each with its
own prefix that builds upon the generic pragma prefix:

*   ``OpenMpPragma`` class defines prefix ``" pragma: omp"`` and stores OpenMP pragmas.
*   ``OpenAccPragma`` class defines prefix ``" pragma: acc"`` and stores OpenACC pragmas.

A code snippet below contains all 3 pragma types.

.. code:: python

    # pragma: once
    use_openmp = True
    use_openacc = True
    ...
    a, b = np.ndarray(...)
    c = np.zeros(...)
    # pragma: acc parallel copyin(a,b) copyout(c)
    # pragma: acc loop gang
    for y in range(ymax): # type: np.int32
        # pragma: acc loop worker
        for i in range(imax): # type: np.int32
            # pragma: acc loop vector reduction(+: c[y][x])
            for x in range(xmax): # type: np.int32
                c[y, x] += a[y, i] * b[i, x]
    # pragma: acc end parallel
    ...
    # pragma: omp parallel do
    for i in range(input_data.size):  # type: int
        # here we compute spam spam spam
        heavy_compute(input_data[i])
    ...

And thus, in the example above:

*   all comments starting with ``" pragma: omp"`` become ``OpenMpPragma`` objects,
*   all comments starting with ``" pragma: acc"`` become ``OpenAccPragma`` objects,
*   all other comments starting with ``" pragma:"`` become ``Pragma`` objects,
*   type comments are ignored, and
*   all other comments become ``Comment`` objects.


Additionally, horast module provides an extensible infrastructure to define
custom ``Pragma`` subclasses, enabling user to define their own pragmas for
experimentation. The provided OpenMP and OpenACC pragma definitions serve
as examples of how to use this feature.


Include
~~~~~~~

Similarly to how pragmas are handled, if a comment begins with ``" include:"``
prefix, it will be classified as a special kind of include directive.

Again, this will be preserved as comment in Python code, but it's useful
for enhancing syntactic compatibility between Python and other, especially
statically compiled languages.


requirements
------------

CPython 3.5 or later.

Python libraries as specified in `<requirements.txt>`_.

Building and running tests additionally requires packages listed in `<test_requirements.txt>`_.
