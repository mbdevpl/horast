"""Unit tests for nodes module."""

import logging
import unittest

import typed_ast.ast3

from horast.nodes import Comment

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    @unittest.skip('eol field is temporarily disabled')
    def test_comment(self):
        expr_fields = typed_ast.ast3.Expr._fields
        comment_fields = Comment._fields
        _LOG.warning('%s', expr_fields)
        _LOG.warning('%s', comment_fields)
        self.assertGreater(len(comment_fields), len(expr_fields))
