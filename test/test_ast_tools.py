"""Unit tests for ast_tools module."""

import unittest

import typed_ast.ast3

from horast.ast_tools import ast_to_list, get_ast_node_locations
from .examples import EXAMPLES


class Tests(unittest.TestCase):

    def test_ast_to_list(self):
        for name, example in EXAMPLES.items():
            for only_localizable in (False, True):
                with self.subTest(name=name, example=example, only_localizable=only_localizable):
                    tree = typed_ast.ast3.parse(example)
                    nodes = ast_to_list(tree, only_localizable)
                    self.assertIsInstance(nodes, list)
                    if tree:
                        self.assertGreaterEqual(len(nodes), 0)

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
