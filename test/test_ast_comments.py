"""Unit tests for ast_comments module."""

import itertools
import unittest

import typed_ast.ast3

from horast.token_tools import get_comment_tokens
from horast.ast_tools import ast_to_list
from horast.ast_comments import insert_comment_tokens, insert_comment_tokens_approx
from .examples import EXAMPLES


class Tests(unittest.TestCase):

    def test_comment_tokens(self):
        only_localizable = False
        for name, example in EXAMPLES.items():
            if ' with eol comments' in name or name.startswith('multiline '):
                continue
            with self.subTest(name=name, example=example):
                tree = insert_comment_tokens(
                    example, typed_ast.ast3.parse(example), get_comment_tokens(example))
                nodes = ast_to_list(tree, only_localizable)
                self.assertIsInstance(tree, typed_ast.ast3.AST)
                non_comment_nodes = ast_to_list(typed_ast.ast3.parse(example), only_localizable)
                comments = get_comment_tokens(example)
                expected_count = max(1 if comments else 0, len(non_comment_nodes)) + len(comments)
                self.assertEqual(len(nodes), expected_count, (nodes, non_comment_nodes, comments))

    @unittest.skip
    def test_comment_tokens_approx(self):
        for (name, example), only_localizable in itertools.product(EXAMPLES.items(), (False, True)):
            # for only_localizable in:
            with self.subTest(name=name, example=example, only_localizable=only_localizable):
                tree = insert_comment_tokens_approx(
                    typed_ast.ast3.parse(example), get_comment_tokens(example))
                nodes = ast_to_list(tree, only_localizable)
                self.assertIsInstance(tree, typed_ast.ast3.AST)
                non_comment_nodes = ast_to_list(typed_ast.ast3.parse(example), only_localizable)
                comments = get_comment_tokens(example)
                expected_count = max(1 if comments else 0, len(non_comment_nodes)) \
                    + (0 if only_localizable else 1) * len(comments)
                self.assertEqual(len(nodes), expected_count, (nodes, non_comment_nodes, comments))
