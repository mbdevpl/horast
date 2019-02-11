"""Unit tests for parser and unparser modules."""

import unittest

import typed_ast.ast3
import typed_astunparse

from horast.ast_tools import ast_to_list
from horast.parser import parse
from horast.unparser import unparse
from .examples import EXAMPLES

MODE_RESULTS = {
    'exec': typed_ast.ast3.Module,
    # 'eval': typed_ast.ast3.expr,
    'single': typed_ast.ast3.Interactive}

TYPE_COMMENT_EXAMPLES = [
    """a = 1""",
    """a = 1  # type: int""",
    """print('abc')""",
    """print('abc')\n# printing abc"""]


class Tests(unittest.TestCase):

    maxDiff = None

    def test_parser_mode(self):
        for mode, result in MODE_RESULTS.items():
            with self.subTest(mode=mode):
                tree = parse('print(1)\n# prints one', mode=mode)
                self.assertIsInstance(tree, result)

    def test_parse_type_comments(self):
        for example in TYPE_COMMENT_EXAMPLES:
            with self.subTest(nexample=example):
                tree = parse(example)
                self.assertIsNotNone(tree)
                code = unparse(tree)
                reparsed_tree = parse(code)
                self.assertIsNotNone(reparsed_tree)
                self.assertEqual(
                    typed_ast.ast3.dump(reparsed_tree), typed_ast.ast3.dump(tree),
                    '"""\n{}\n""" vs. original """\n{}\n"""'.format(code, example))
                self.assertEqual(code.strip(), example)

    def test_parse(self):
        for name, example in EXAMPLES.items():
            if ' with eol comments' in name or name.startswith('multiline '):
                continue
            with self.subTest(name=name, example=example):
                tree = parse(example)
                self.assertIsNotNone(tree)

    def test_single_line(self):
        code = """a = 1  # a equals one after this"""
        tree = parse(code)
        unparsed = unparse(tree).strip()
        self.assertEqual(unparsed, code)

    def test_parse_failure(self):
        with self.assertRaises(SyntaxError):
            parse('def ill_pass(): pass', mode='eval')

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
            data = {}
            with self.subTest(name=name, example=example, data=data):
                tree = typed_ast.ast3.parse(example)
                code = typed_astunparse.unparse(tree)
                complete_tree = parse(example)
                data['complete_tree'] = complete_tree
                complete_code = unparse(complete_tree)
                data['complete_code'] = complete_code
                self.assertGreaterEqual(
                    len(complete_code.replace(' ', '')), len(code.replace(' ', '')),
                    (complete_code, code))
                reparsed_tree = typed_ast.ast3.parse(code)
                tree_nodes = ast_to_list(tree, only_localizable)
                reparsed_tree_nodes = ast_to_list(reparsed_tree, only_localizable)
                self.assertEqual(len(reparsed_tree_nodes), len(tree_nodes))
                self.assertEqual(typed_ast.ast3.dump(reparsed_tree), typed_ast.ast3.dump(tree))
                reparsed_complete_tree = parse(complete_code)
                complete_tree_nodes = ast_to_list(complete_tree, only_localizable)
                reparsed_complete_tree_nodes = ast_to_list(reparsed_complete_tree, only_localizable)
                self.assertEqual(
                    len(reparsed_complete_tree_nodes), len(complete_tree_nodes), complete_code)
                self.assertEqual(
                    typed_ast.ast3.dump(reparsed_complete_tree),
                    typed_ast.ast3.dump(complete_tree),
                    '"""\n{}\n""" vs. original """\n{}\n"""'.format(complete_code, example))
