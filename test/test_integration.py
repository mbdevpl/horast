"""Integration tests for all modules."""

import logging
import unittest

import typed_ast.ast3

from horast.nodes import Comment, Directive
from horast.unparser import unparse

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    def test_unparse_comment(self):
        tree = typed_ast.ast3.If(
            typed_ast.ast3.NameConstant(True),
            [typed_ast.ast3.Pass(), Comment(typed_ast.ast3.Str(' hello world', ''), eol=False)], [])
        code = unparse(tree)
        self.assertEqual(code.strip(), 'if True:\n    pass\n    # hello world')

    def test_unparse_eol_comment(self):
        tree = typed_ast.ast3.If(
            typed_ast.ast3.NameConstant(True),
            [typed_ast.ast3.Pass(), Comment(typed_ast.ast3.Str(' hello world', ''), eol=True)], [])
        code = unparse(tree)
        self.assertEqual(code.strip(), 'if True:\n    pass  # hello world')

    def test_unparse_directive(self):
        tree = typed_ast.ast3.If(
            typed_ast.ast3.NameConstant(True),
            [Directive(typed_ast.ast3.Str('include<thisisnotcpp>', '')), typed_ast.ast3.Pass()], [])
        code = unparse(tree)
        self.assertEqual(code.strip(), 'if True:\n    #include<thisisnotcpp>\n    pass')
