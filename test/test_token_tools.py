"""Unit tests for ast_comments module."""

import tokenize
import unittest

from horast.token_tools import get_tokens
from .examples import EXAMPLES


class Tests(unittest.TestCase):

    def test_get_comment_tokens(self):
        for name, example in EXAMPLES.items():
            with self.subTest(name=name, example=example):
                tokens = get_tokens(example)
                self.assertIsInstance(tokens, list)
                for token in tokens:
                    self.assertIsInstance(token, tokenize.TokenInfo)
