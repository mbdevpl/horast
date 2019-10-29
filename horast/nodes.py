"""Definitions of AST nodes used to store missing syntax information."""

# pylint: disable=too-few-public-methods

import logging
import tokenize
import typing as t

import typed_ast.ast3

from .token_tools import get_token_scope

_LOG = logging.getLogger(__name__)


class Comment(typed_ast.ast3.AST):
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

    _fields = typed_ast.ast3.AST._fields + ('comment', 'eol')

    @staticmethod
    def is_eol(token: tokenize.TokenInfo, path_to_anchor, before_anchor) -> bool:
        """Determine if a given comment token is an end-of-line comment or not."""
        if before_anchor:
            return False
        assert path_to_anchor
        anchor = path_to_anchor[-1]
        assert isinstance(anchor.field, str), type(anchor.field)
        node = getattr(anchor.node, anchor.field)
        if anchor.index is not None:
            node = node[anchor.index]
        if not hasattr(node, 'lineno'):
            raise ValueError('anchor node {} must have "lineno" attribute'
                             .format(typed_ast.ast3.dump(node, include_attributes=True)))
        token_scope = get_token_scope(token)
        assert token_scope.start.lineno == token_scope.end.lineno, token_scope
        assert token_scope.start.offset < token_scope.end.offset, token_scope
        eol = anchor.scope.end.lineno == token_scope.start.lineno
        _LOG.debug('comment scope: %s, anchor scope: %s, evaluated EOL status: %s',
                   (token.start[0], token.end[0], token_scope), (node.lineno, anchor.scope), eol)
        return eol

    @classmethod
    def from_token(cls, token: tokenize.TokenInfo, path_to_anchor, before_anchor):
        eol = cls.is_eol(token, path_to_anchor, before_anchor)
        return cls(
            comment=token.string[1:], eol=eol,
            lineno=token.start[0], col_offset=token.start[1])


class BlockComment(typed_ast.ast3.AST):
    """Store sequence of code comments as a single node in AST.

    Example:

    # 1st line of a comment
    # 2nd line of a comment
    # 3rd line of a comment
    """

    _fields = typed_ast.ast3.AST._fields + ('comments',)

    @classmethod
    def from_token(cls, token: tokenize.TokenInfo, *extra_tokens: t.List[tokenize.TokenInfo]):
        raise NotImplementedError()


class Directive(typed_ast.ast3.AST):
    """Store directive in AST.

    In Python, directives would be expressed as comments, but may have special additional meaning.

    Examples:

    #if
    #else
    #endif
    #def
    #undef
    #ifdef
    #ifndef
    """

    _comment_prefixes = ('if', 'else', 'endif', 'def', 'undef', 'ifdef', 'ifndef')

    _fields = typed_ast.ast3.AST._fields + ('expr',)

    @classmethod
    def from_token(cls, token: tokenize.TokenInfo):
        """Create a Directive from a comment token."""
        expr = token.string[1:]
        if len(cls._comment_prefixes) == 1:
            prefix = cls._comment_prefixes[0]
            assert expr.startswith(prefix), expr
            _LOG.debug(
                'stripping prefix "%s" and following whitespace from the token %s', prefix, token)
            expr = expr[len(prefix):].lstrip()
        return cls(
            expr=expr,
            lineno=token.start[0], col_offset=token.start[1])


class Pragma(Directive):
    """Store a pragma in AST.

    Examples:

    # pragma: once
    # pragma: ...
    """

    _comment_prefixes = (' pragma:',)


class OpenMpPragma(Pragma):
    """A special node for storing OpenMP pragmas in AST.

    Examples:

    # pragma: omp parallel for
    """

    _comment_prefixes = (' pragma: omp',)


class OpenAccPragma(Pragma):
    """A special node for storing OpenACC pragmas in AST.

    Examples:

    # pragma: acc parallel
    """

    _comment_prefixes = (' pragma: acc',)


class Include(Directive):
    """Store an include directive in AST.

    # include: <cstdio>
    # include: "mpif.h"
    # include: my_header.h
    """

    _comment_prefixes = (' include:',)
