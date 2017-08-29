"""Unit tests for ast_comments module."""

import unittest

import typed_ast.ast3

from horast.ast_tools import ast_to_list
from horast.ast_comments import get_comment_tokens, insert_comment_tokens
from test.examples import EXAMPLES


class Tests(unittest.TestCase):

    def test_insert_comment_tokens(self):
        for name, example in EXAMPLES.items():
            for only_localizable in (False, True):
                with self.subTest(name=name, example=example, only_localizable=only_localizable):
                    tree = insert_comment_tokens(
                        typed_ast.ast3.parse(example), get_comment_tokens(example))
                    tree_nodes = ast_to_list(tree, only_localizable)
                    self.assertIsInstance(tree, typed_ast.ast3.AST)
                    nodes = ast_to_list(typed_ast.ast3.parse(example), only_localizable)
                    comments = get_comment_tokens(example)
                    self.assertEqual(
                        len(tree_nodes), max(1 if comments else 0, len(nodes)) + 2 * len(comments),
                        (tree_nodes, nodes, comments))
