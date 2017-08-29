"""Various helper functions to query and manipulate tokens."""

import io
import tokenize
import typing as t


def get_tokens(code: str) -> t.List[tokenize.TokenInfo]:
    assert isinstance(code, str), type(code)
    code_bytes = code.encode() # type: bytes
    with io.BytesIO(code_bytes) as code_bytes_reader:
        tokenizer = tokenize.tokenize(code_bytes_reader.readline)
        tokens = [token for token in tokenizer]
    return tokens


def get_token_locations(tokens: t.List[tokenize.TokenInfo]) -> t.List[t.Tuple[int, int]]:
    return [token.start for token in tokens]
