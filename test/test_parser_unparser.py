"""Unit tests for parser and unparser modules."""

import unittest

import typed_ast.ast3
import typed_astunparse

from horast.ast_tools import ast_to_list
from horast.parser import parse
from horast.unparser import unparse
from .examples import EXAMPLES


class Tests(unittest.TestCase):

    maxDiff = None

    def test_parse(self):
        for name, example in EXAMPLES.items():
            if ' with eol comments' in name or name.startswith('multiline '):
                continue
            with self.subTest(name=name, example=example):
                tree = parse(example)
                self.assertIsNotNone(tree)

    def test_roundtrip_without_comments(self):
        for name, example in EXAMPLES.items():
            with self.subTest(name=name, example=example):
                tree = typed_ast.ast3.parse(example)
                code = unparse(tree)
                reparsed_tree = typed_ast.ast3.parse(code)
                self.assertEqual(typed_ast.ast3.dump(reparsed_tree), typed_ast.ast3.dump(tree))

    def test_roundtrip(self):
        only_localizable = False
        for name, example in EXAMPLES.items():
            if ' with eol comments' in name or name.startswith('multiline '):
                continue
            with self.subTest(name=name, example=example):
                tree = typed_ast.ast3.parse(example)
                code = typed_astunparse.unparse(tree)
                complete_tree = parse(example)
                complete_code = unparse(complete_tree)
                self.assertGreaterEqual(len(complete_code), len(code), (complete_code, code))
                reparsed_tree = typed_ast.ast3.parse(code)
                tree_nodes = ast_to_list(tree, only_localizable)
                reparsed_tree_nodes = ast_to_list(reparsed_tree, only_localizable)
                self.assertEqual(len(reparsed_tree_nodes), len(tree_nodes))
                self.assertEqual(typed_ast.ast3.dump(reparsed_tree), typed_ast.ast3.dump(tree))
                try:
                    reparsed_complete_tree = parse(complete_code)
                except SyntaxError as err:
                    raise AssertionError('invalid syntax after inserting comments:\n{}'.format(
                        typed_ast.ast3.dump(complete_tree))) from err
                complete_tree_nodes = ast_to_list(complete_tree, only_localizable)
                reparsed_complete_tree_nodes = ast_to_list(reparsed_complete_tree, only_localizable)
                self.assertEqual(
                    len(reparsed_complete_tree_nodes), len(complete_tree_nodes), complete_code)
                self.assertEqual(
                    typed_ast.ast3.dump(reparsed_complete_tree),
                    typed_ast.ast3.dump(complete_tree),
                    '"""\n{}\n""" vs. original """\n{}\n"""'.format(complete_code, example))
