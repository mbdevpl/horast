"""Definitions of AST nodes used to store missing syntax information."""

# pylint: disable=too-few-public-methods

import tokenize
import typing as t

import typed_ast.ast3


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

    pass


class Docstring(typed_ast.ast3.Expr):

    """Store docstring as a special node in AST."""

    @classmethod
    def from_str_expr(cls, str_expr: typed_ast.ast3.Expr):
        raise NotImplementedError()
