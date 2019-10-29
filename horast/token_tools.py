"""Various helper functions to query and manipulate tokens."""

import io
import tokenize
import typing as t
import warnings

Location = t.NamedTuple('Location', [('lineno', int), ('offset', int)])

Scope = t.NamedTuple('Scope', [('start', t.Tuple[int, int]), ('end', t.Tuple[int, int])])


def get_token_scope(token: tokenize.TokenInfo):
    return Scope(Location(*token.start), Location(*token.end))


def get_tokens(code: str, token_filter=None) -> t.List[tokenize.TokenInfo]:
    """List of all tokens contained in the given code."""
    assert isinstance(code, str), type(code)
    code_bytes = code.encode()  # type: bytes
    with io.BytesIO(code_bytes) as code_bytes_reader:
        tokenizer = tokenize.tokenize(code_bytes_reader.readline)
        tokens = [token for token in tokenizer if token_filter is None or token_filter(token)]
    return tokens


def is_comment(token: tokenize.TokenInfo) -> bool:
    return token.type is tokenize.COMMENT


def is_type_comment(token: tokenize.TokenInfo) -> bool:
    return token.string.startswith('# type:') and token.string != '# type: ignore'


def is_comment_but_not_type_comment(token: tokenize.TokenInfo) -> bool:
    return is_comment(token) and not is_type_comment(token)


def get_comment_tokens(code: str, ignore_type_comments: bool = True) -> t.List[tokenize.TokenInfo]:
    return get_tokens(code, is_comment_but_not_type_comment if ignore_type_comments else is_comment)


def get_token_locations(tokens: t.List[tokenize.TokenInfo]) -> t.List[t.Tuple[int, int]]:
    warnings.warn('function get_token_locations is obsolete and it will be removed from horast,'
                  ' use get_token_scope instead', DeprecationWarning)
    return [token.start for token in tokens]
