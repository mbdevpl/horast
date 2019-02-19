"""Definitions of AST nodes used to store missing syntax information."""

# pylint: disable=too-few-public-methods

import itertools
import logging
import tokenize
import typing as t

import typed_ast.ast3

# from .token_tools import get_tokens

_LOG = logging.getLogger(__name__)


def _comment_token_to_ast_node(token: tokenize.TokenInfo) -> typed_ast.ast3.Str:
    """Convert comment token to its raw AST representation."""
    return typed_ast.ast3.Str(s=token.string[1:], kind='',
                              lineno=token.start[0], col_offset=token.start[1] + 1)


_preprocessor_directives = {('if',), ('endif',), ('def',), ('undef',), ('ifdef',)}

_openmp_for_clauses = (
    'private', 'rstprivate', 'lastprivate', 'reduction', 'schedule', 'collapse', 'ordered',
    'nowait')

_openmp_parallel_clauses = (
    'if', 'num_threads', 'default', 'private', 'rstprivate', 'shared', 'copyin', 'reduction')

_common_openmp_prefixes = [
    ('target',), ('distribute',), ('teams', 'distribute'), ('target', 'teams', 'distribute')]

_common_openmp_suffixes = [('simd',), ('parallel', 'for'), ('parallel', 'for', 'simd')]

_openmp_pragmas = {
    ('parallel',),
    ('for',), ('parallel', 'for',),

    ('sections',), ('parallel', 'sections'), ('section',),

    ('simd',), ('for', 'simd'), ('parallel', 'for', 'simd'), ('declare', 'simd'),

    ('task',), ('taskloop',), ('taskloop', 'simd'), ('taskyield',),

    ('target',), ('target', 'data'), ('target', 'enter', 'data'), ('target', 'exit', 'data'),
    ('target', 'update'), ('declare', 'target'), ('target', 'parallel'),
    # ('target', 'simd'),
    # ('target', 'parallel', 'for'),
    # ('target', 'parallel', 'for', 'simd'),

    ('distribute',),
    # ('distribute', 'simd'),
    # ('distribute', 'parallel', 'for'),
    # ('distribute', 'parallel', 'for', 'simd'),

    ('teams',), ('teams', 'distribute'),
    # ('teams', 'distribute', 'simd'),
    # ('teams', 'distribute', 'parallel', 'for'),
    # ('teams', 'distribute', 'parallel', 'for', 'simd'),
    ('target', 'teams'), ('target', 'teams', 'distribute'),
    # ('target', 'teams', 'distribute', 'simd'),
    # ('target', 'teams', 'distribute', 'parallel', 'for'),
    # ('target', 'teams', 'distribute', 'parallel', 'for', 'simd'),

    ('single',), ('master',), ('critical',), ('barrier',),

    ('taskwait',), ('tastkgroup',), ('atomic',), ('flush',), ('ordered',),
    ('cancel',), ('cancellation', 'point'), ('threadprivate',), ('declare', 'reduction')} \
    | {tuple(list(prefix) + list(suffix)) for (prefix, suffix) in
       itertools.product(_common_openmp_prefixes, _common_openmp_suffixes)}

_openacc_parallel_clauses = {
    'if', 'self', 'default', 'default', 'device_typeordtype', 'async',
    'wait', 'num_gangs', 'num_workers', 'vector_length', 'reduction',
    'private', 'firstprivate',
    'copy', 'copyin', 'copyout', 'create', 'no_create', 'present', 'deviceptr', 'attach'}

_openacc_pragmas = {
    ('parallel'), ('kernels'), ('serial'), ('data'),
    ('host_data'),
    ('atomic',)}

_openacc_pragmas |= {('end', _) for _ in _openacc_pragmas} \
    | {('enter', 'data'), ('exit', 'data'), ('loop',), ('cache',), ('update',), ('wait',)}

_allowed_prefixes = \
    _preprocessor_directives \
    | {('pragma', 'omp', *_) for _ in _openmp_pragmas} \
    | {('pragma', 'acc', *_) for _ in _openacc_pragmas}

_allowed_prefixes_max_len = max(len(_) for _ in _allowed_prefixes)


def _comment_token_to_directive_prefix(token: tokenize.TokenInfo) -> typed_ast.ast3.Tuple:
    raw_value = token.string[1:]
    if raw_value.startswith(' '):
        raise ValueError('directive "{}" begins with whitespace'.format(raw_value))
    # raw_value_tokens = get_tokens(raw_value)
    raw_value_tokens = raw_value.split()
    _LOG.warning('directive "%s" tokenized into %s', raw_value, raw_value_tokens)
    prefix = None
    for length in range(_allowed_prefixes_max_len, 0, -1):
        prefix_candidate = tuple(raw_value_tokens[:length])
        if prefix_candidate in _allowed_prefixes:
            prefix = prefix_candidate
            break
    if prefix is None:
        raise ValueError('directive "{}" is not allowed'.format(raw_value))
    return typed_ast.ast3.Tuple(
        elts=prefix, lineno=token.start[0] + 1, col_offset=token.start[1])


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
    #pragma omp parallel for
    #pragma acc loop
    """

    _fields = typed_ast.ast3.Expr._fields + ('prefix',)

    @classmethod
    def from_token(cls, token: tokenize.TokenInfo):
        prefix = _comment_token_to_directive_prefix(token)
        prefix_end = 1
        for _ in prefix.elts:
            try:
                prefix_end = token.string.index(_, prefix_end) + len(_)
            except ValueError as error:
                raise SyntaxError() from error
        raw_prefix = token.string[1:prefix_end]
        raw_value = token.string[prefix_end:]
        stripped_value = raw_value.lstrip()
        offset = len(raw_value) - len(stripped_value)
        _LOG.warning('got directive prefix="%s" value="%s"', raw_prefix, stripped_value)

        if stripped_value:
            try:
                value = typed_ast.ast3.parse(stripped_value, mode='eval')
            except Exception as error:
                raise SyntaxError('failed to parse "{}"'.format(stripped_value)) from error
            value.lineno = token.start[0]
            value.col_offset = token.start[0] + 1 + len(raw_prefix) + offset
        else:
            value = typed_ast.ast3.Str('', '')

        return cls(
            value=value, prefix=prefix,
            lineno=token.start[0], col_offset=token.start[1])


class Docstring(typed_ast.ast3.Expr):

    """Store docstring as a special node in AST."""

    @classmethod
    def from_str_expr(cls, str_expr: typed_ast.ast3.Expr):
        raise NotImplementedError()
