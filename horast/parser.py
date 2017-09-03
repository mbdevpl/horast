"""Extension of typed_ast parser for Python 3 that retains comments in the AST."""

import typed_ast.ast3

from .token_tools import get_comment_tokens
from .ast_comments import insert_comment_tokens


def parse(code: str, *args, **kwargs) -> typed_ast.ast3.AST:
    """Parse given code into AST based on typed_ast.ast3 with nodes as defined in horast.nodes."""
    assert isinstance(code, str), type(code)
    try:
        tree = typed_ast.ast3.parse(code, *args, **kwargs)
    except SyntaxError as err:
        raise SyntaxError('typed_ast.ast3.parse(code{}{}) failed on code:\n"""\n{}\n"""'.format(
            (', args=' + str(args)) if args else '', (', kwargs=' + str(kwargs)) if kwargs else '',
            code)) from err
    comment_tokens = get_comment_tokens(code)
    tree = insert_comment_tokens(code, tree, comment_tokens)
    return tree
