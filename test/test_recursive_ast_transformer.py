"""Unit tests for RecursiveAstVisitor."""

import unittest

import typed_ast.ast3

from horast.recursive_ast_transformer import RecursiveAstTransformer
from horast.ast_tools import ast_to_list
from .examples import EXAMPLES


class Tests(unittest.TestCase):

    def test_visit(self):
        for name, example in EXAMPLES.items():
            with self.subTest(name=name, example=example):
                def transform(node):
                    if isinstance(node, (typed_ast.ast3.expr, typed_ast.ast3.stmt, typed_ast.ast3.arg)):
                        node.lineno = 42
                    return node
                visitor = RecursiveAstTransformer(transform)
                initial_tree = typed_ast.ast3.parse(example)
                initial_nodes = ast_to_list(initial_tree)
                tree = visitor.visit(initial_tree)
                nodes = ast_to_list(tree)
                self.assertEqual(len(initial_nodes), len(nodes))
                for node in nodes:
                    if hasattr(node, 'lineno'):
                        self.assertEqual(node.lineno, 42, (type(node), node))
