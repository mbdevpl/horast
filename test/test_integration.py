"""Integration tests for all modules."""

import logging
import unittest

import typed_ast.ast3

from horast.nodes import Directive
from horast.unparser import unparse

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    def test_unparse_directive(self):
        tree = typed_ast.ast3.If(
            typed_ast.ast3.NameConstant(True),
            [Directive(typed_ast.ast3.Str('include<thisisnotcpp>', '')), typed_ast.ast3.Pass()], [])
        code = unparse(tree)
        self.assertEqual(code.strip(), 'if True:\n    #include<thisisnotcpp>\n    pass')
