"""Unit tests for ast_tools module."""

import unittest

import typed_ast.ast3

from horast.token_tools import Scope, get_comment_tokens, get_token_scopes
from horast.ast_tools import \
    ast_to_list, get_ast_node_locations, convert_1d_str_index_to_2d, get_ast_node_scopes, \
    find_in_ast
from .examples import EXAMPLES


class Tests(unittest.TestCase):

    def test_ast_to_list(self):
        for name, example in EXAMPLES.items():
            for only_localizable in (False, True):
                with self.subTest(name=name, example=example, only_localizable=only_localizable):
                    tree = typed_ast.ast3.parse(example)
                    nodes = ast_to_list(tree, only_localizable)
                    self.assertIsInstance(nodes, list)
                    if not only_localizable:
                        self.assertGreater(len(nodes), 0)

    def test_get_ast_node_locations(self):
        for name, example in EXAMPLES.items():
            for only_localizable in (False, True):
                with self.subTest(name=name, example=example, only_localizable=only_localizable):
                    tree = typed_ast.ast3.parse(example)
                    nodes = ast_to_list(tree, only_localizable)
                    locations = get_ast_node_locations(nodes)
                    self.assertIsInstance(locations, list)
                    for location in locations:
                        self.assertIsInstance(location, tuple)
                        self.assertEqual(len(location), 2)

    def test_convert_1d_str_index_to_2d(self):
        texts = [
            'def', 'def\n', 'def\nghi', '\ndef\nghi', 'abc\ndef\nghi',
            '', '\n', '\n\n']
        for text in texts:
            for index in range(len(text) + 1):
                with self.subTest(text=text, index=index):
                    location = convert_1d_str_index_to_2d(text, index)
                    lineno, col_offset = location
                    self.assertGreaterEqual(lineno, 1, location)
                    self.assertGreaterEqual(col_offset, 0, location)
                    lines = text.splitlines(keepends=True)
                    if not text or text.endswith('\n'):
                        lines += ['']
                    self.assertLessEqual(lineno, len(lines))
                    line = lines[lineno - 1]
                    self.assertLessEqual(
                        col_offset, len(line), 'line no.{} is {}'.format(lineno, repr(line)))
                    if col_offset < len(line):
                        self.assertEqual(line[col_offset], text[index])
                    else:
                        self.assertGreaterEqual(
                            lineno, len(lines),
                            'location {} oveflows into the next line in line no.{} {}'
                            .format(location, lineno, repr(line)))

    def test_get_ast_node_scopes(self):
        for name, example in EXAMPLES.items():
            with self.subTest(name=name, example=example):
                tree = typed_ast.ast3.parse(example)
                nodes = ast_to_list(tree)
                scopes = get_ast_node_scopes(example, nodes)
                self.assertIsInstance(scopes, list)
                self.assertEqual(len(scopes), len(nodes))
                for scope in scopes:
                    self.assertIsInstance(scope, Scope)
                locations = get_ast_node_locations(nodes)
                self.assertEqual(len(scopes), len(locations))
                for node, scope, location in zip(nodes, scopes, locations):
                    if None in location:
                        continue
                    self.assertEqual(scope.start, location, '{} in: """\n{}\n"""'.format(
                        typed_ast.ast3.dump(node), example))

    def test_find_in_ast(self):
        for name, example in EXAMPLES.items():
            if ' with eol comments' in name or name.startswith('multiline '):
                continue
            for index in range(0, len(example) + 1, 64):
                for end_index in range(index + 1, len(example) + 1, 64):
                    # TODO: decrease distance step without failing assertions
                    scope = Scope(convert_1d_str_index_to_2d(example, index),
                                  convert_1d_str_index_to_2d(example, end_index))
                    with self.subTest(name=name, example=example, scope=scope):
                        tree = typed_ast.ast3.parse(example)
                        nodes = ast_to_list(tree)
                        path, before = find_in_ast(example, tree, nodes, scope)
                        self.assertIsInstance(path, list)
                        self.assertIsInstance(before, bool)

    def test_find_in_ast_real(self):
        for name, example in EXAMPLES.items():
            if ' with eol comments' in name or name.startswith('multiline '):
                continue
            comment_tokens = get_comment_tokens(example)
            scopes = get_token_scopes(comment_tokens)
            for scope in scopes:
                with self.subTest(name=name, example=example, scope=scope):
                    tree = typed_ast.ast3.parse(example)
                    nodes = ast_to_list(tree)
                    path, before = find_in_ast(example, tree, nodes, scope)
                    self.assertIsInstance(path, list)
                    self.assertIsInstance(before, bool)
