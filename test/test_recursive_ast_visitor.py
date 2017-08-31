"""Unit tests for RecursiveAstVisitor."""

import unittest

import typed_ast.ast3

from horast.recursive_ast_visitor import RecursiveAstVisitor
from .examples import EXAMPLES


class Tests(unittest.TestCase):

    def test_visit(self):
        for name, example in EXAMPLES.items():
            with self.subTest(name=name, example=example):
                nodes = []
                def accumulate(node):
                    nodes.append(node)
                visitor = RecursiveAstVisitor(accumulate)
                visitor.visit(typed_ast.ast3.parse(example))
                self.assertGreater(len(nodes), 0)
