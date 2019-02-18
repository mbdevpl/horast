"""Definitions of AST nodes used to store missing syntax information."""

# pylint: disable=too-few-public-methods

import logging
import tokenize
import typing as t

import typed_ast.ast3

from .token_tools import get_tokens

_LOG = logging.getLogger(__name__)


def _comment_token_to_ast_node(token: tokenize.TokenInfo) -> typed_ast.ast3.Str:
    """Convert comment token to its raw AST representation."""
    return typed_ast.ast3.Str(s=token.string[1:], kind='',
                              lineno=token.start[0], col_offset=token.start[1] + 1)


class Comment(typed_ast.ast3.Expr):

    """Store code comment in AST.

    Examples:

    # full line comment

    expr # end-of-line comment

    (value1,
     # full line comment inside an expression
     value2,
     value3)

    (value1,
     value2,  # end-of line comment inside an expression
     value3)
    """

    _fields = typed_ast.ast3.Expr._fields + ('eol',)

    @classmethod
    def from_token(cls, token: tokenize.TokenInfo, eol: bool):
        return cls(
            value=_comment_token_to_ast_node(token), eol=eol,
            lineno=token.start[0], col_offset=token.start[1])


class BlockComment(typed_ast.ast3.Expr):

    """Store sequence of code comments as a single node in AST.

    Example:

    # 1st line of a comment
    # 2nd line of a comment
    # 3rd line of a comment
    """

    @classmethod
    def from_tokens(cls, tokens: t.List[tokenize.TokenInfo]):
        return cls(
            value=typed_ast.ast3.Tuple(
                elts=[_comment_token_to_ast_node(token) for token in tokens],
                lineno=tokens[0].start[0], col_offset=tokens[0].start[1]),
            lineno=tokens[0].start[0], col_offset=tokens[0].start[1])


class Directive(typed_ast.ast3.Expr):

    """Store directive in AST.

    In Python, directives would be expressed as comments, but may have special additional meaning.

    Examples:

    #if
    #endif
    #def
    #undef
    #ifdef
    #pragma omp parallel loop
    #pragma acc
    """

    _allowed_prefixes = {
        ('if',),
        ('endif',),
        ('def',),
        ('undef',),
        ('ifdef',),
        ('pragma',),
        ('pragma', 'omp', 'parallel'),
        ('pragma', 'acc')}

    _fields = typed_ast.ast3.Expr._fields + ('prefixes',)

    @classmethod
    def from_token(cls, token: tokenize.TokenInfo):
        raw_value = token.string[1:]
        raw_value_tokens = get_tokens(raw_value)
        _LOG.warning('%s', raw_value_tokens)
        # atok = asttokens.ASTTokens(code, tree=ast.parse(code))
        # (s=, kind='', lineno=token.start[0], col_offset=token.start[1] + 1)
        # value = typed_ast.ast3.parse(raw_value, mode='expr')
        # value = (token)
        # prefixes = ('',)
        prefixes_len = 0
        try:
            # value.lineno += prefixes_len
            raise NotImplementedError()
        except:
            value = _comment_token_to_ast_node(token)
            prefixes = ()
        return cls(
            value=value, prefixes=typed_ast.ast3.Tuple(
                elts=prefixes, lineno=token.start[0] + 1, col_offset=token.start[1]),
            lineno=token.start[0], col_offset=token.start[1])


class Docstring(typed_ast.ast3.Expr):

    """Store docstring as a special node in AST."""

    @classmethod
    def from_str_expr(cls, str_expr: typed_ast.ast3.Expr):
        raise NotImplementedError()
