"""Unit tests for nodes module."""

import logging
import unittest

import typed_ast.ast3

from horast.nodes import Comment

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    def test_comment(self):
        expr_fields = typed_ast.ast3.Expr._fields
        comment_fields = Comment._fields
        _LOG.warning('%s', expr_fields)
        _LOG.warning('%s', comment_fields)
        self.assertGreater(len(comment_fields), len(expr_fields))

        comment = Comment(typed_ast.ast3.Str(' comment', ''), False)
        self.assertFalse(comment.eol)

        eol_comment = Comment(typed_ast.ast3.Str(' comment', ''), True)
        self.assertTrue(eol_comment.eol)

        default_comment = Comment(typed_ast.ast3.Str(' comment', ''))
        with self.assertRaises(AttributeError):
            default_comment.eol
