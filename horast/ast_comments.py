"""Extract comments from untouched source code and insert them into the AST."""

import logging
import tokenize
import typing as t
import warnings

import typed_ast.ast3
import typed_astunparse

from .nodes import Comment, Directive, Pragma, OpenMpPragma, OpenAccPragma, Include
from .token_tools import get_token_scope, get_token_locations  # , get_token_scopes
from .ast_tools import \
    ast_to_list, get_ast_node_locations, get_ast_node_scopes, find_in_ast, \
    insert_at_path_in_tree, insert_in_tree

_LOG = logging.getLogger(__name__)

CLASSIFIED_NODES = (Include, OpenMpPragma, OpenAccPragma, Pragma, Directive)


def is_prefixed(text: str, prefix: str) -> bool:
    """Check if a text (assumed to be a token value) is prefixed with a given prefix.

    This is different from simple checking text.startswith(prefix),
    because it also applies criteria normally applied by tokenizer to separate tokens.

    E.g. "acc loop" is prefixed with "acc", but "accelerate" is not.
    """
    if not text.startswith(prefix):
        return False
    if len(text) == len(prefix) or prefix[-1] == ':':
        return True
    return any(text[len(prefix):].startswith(_) for _ in (' ', '('))


def classify_comment_token(token: tokenize.TokenInfo) -> type:
    # for node_type, prefixes in PREFIXES:
    for node_type in CLASSIFIED_NODES:
        # for prefix in prefixes:
        for prefix in getattr(node_type, '_comment_prefixes', ()):
            if is_prefixed(token.string[1:], prefix):
                _LOG.debug('classified "%s" as %s (prefix: %s)', token.string, node_type, prefix)
                return node_type
    _LOG.debug('classified "%s" as %s', token.string, Comment)
    return Comment


def insert_comment_token(token: tokenize.TokenInfo, code: str, tree: typed_ast.ast3.AST,
                         *, nodes=None, scopes=None):
    """Insert comment into the syntax tree.

    Last 2 argument "nodes" and "scopes" are optional but when calling this function many times
    for the same AST providing them is encouraged as constructing those lists is time consuming.
    """
    if nodes is None:
        nodes = ast_to_list(tree)
    if scopes is None:
        scopes = get_ast_node_scopes(code, nodes)
    scope = get_token_scope(token)
    path_to_anchor, before_anchor = find_in_ast(code, tree, scope, nodes=nodes, scopes=scopes)
    node_type = classify_comment_token(token)
    if issubclass(node_type, Comment):
        node = node_type.from_token(token, path_to_anchor, before_anchor)
    else:
        if issubclass(node_type, Directive):
            node = node_type.from_token(token)
        else:
            raise ValueError('insertion of node {} (from token "{}") is not supported'
                             .format(node_type.__name__, token))

    _LOG.debug('inserting a %s: %s %s %s', type(node).__name__, node,
               'before' if before_anchor else 'after', path_to_anchor[-1])
    return insert_at_path_in_tree(tree, node, path_to_anchor, before_anchor)


def insert_comment_tokens(
        code: str, tree: typed_ast.ast3.AST,
        tokens: t.List[tokenize.TokenInfo]) -> typed_ast.ast3.AST:
    """Insert comment tokens into an AST obtained from typed_ast parser."""
    assert isinstance(tree, typed_ast.ast3.AST)
    assert isinstance(tokens, list)
    nodes = ast_to_list(tree)
    scopes = get_ast_node_scopes(code, nodes)
    assert len(nodes) == len(scopes), (len(nodes), len(scopes))
    for token in tokens:
        tree = insert_comment_token(token, code, tree, nodes=nodes, scopes=scopes)
    return tree


def insert_comment_tokens_approx(
        tree: typed_ast.ast3.AST, tokens: t.List[tokenize.TokenInfo]) -> typed_ast.ast3.AST:
    """Deprecated, use insert_comment_tokens instead."""
    warnings.warn('function insert_comment_tokens_approx is outdated and faulty, and it will be'
                  ' removed from horast, use insert_comment_tokens instead', DeprecationWarning)
    assert isinstance(tree, typed_ast.ast3.AST)
    assert isinstance(tokens, list)
    token_locations = get_token_locations(tokens)
    _LOG.debug('token locations: %s', token_locations)
    nodes = ast_to_list(tree, only_localizable=True)
    if not nodes and tokens:
        _LOG.debug('overwriting empty AST with simplest editable tree')
        tree = typed_ast.ast3.Module(body=[], type_ignores=[], lineno=1, col_offset=0)
        nodes = ast_to_list(tree, only_localizable=True)
    node_locations = get_ast_node_locations(nodes)
    _LOG.debug('node locations: %s', node_locations)
    node_locations_iter = enumerate(node_locations)
    token_insertion_indices = []
    tokens_eol_status = []
    for token_index, token_location in enumerate(token_locations):
        eol_comment_here = False
        try:
            node_index, node_location = next(node_locations_iter)
        except StopIteration:
            node_index = len(node_locations)
            node_location = None
        while node_location is not None:
            token_line, _ = token_location
            node_line, _ = node_location
            if node_line > token_line:
                break
            if node_line == token_line:
                eol_comment_here = True
                if node_index < len(node_locations) - 1:
                    next_node_line, _ = node_locations[node_index + 1]
                    if next_node_line == token_line:
                        eol_comment_here = False
                # if eol_comment_here:
                #    raise NotImplementedError(
                #        'code "{}" and comment "{}" in line {}'
                #        ' -- only whole line comments are currently supported'
                #        .format(typed_astunparse.unparse(nodes[node_index]).strip(),
                #                tokens[token_index].string, node_line))
            try:
                node_index, node_location = next(node_locations_iter)
            except StopIteration:
                node_index = len(node_locations)
                break
        tokens_eol_status.append(eol_comment_here)
        token_insertion_indices.append(node_index)
    _LOG.debug('token insertion indices: %s', token_insertion_indices)
    _LOG.debug('tree before insertion:\n"""\n%s\n"""', typed_astunparse.dump(tree))
    _LOG.debug('code before insertion:\n"""\n%s\n"""', typed_astunparse.unparse(tree).strip())
    for token_index, token_insertion_index in reversed(list(enumerate(token_insertion_indices))):
        token = tokens[token_index]
        eol = tokens_eol_status[token_index]
        comment = Comment(token.string[1:], eol)
        if token_insertion_index == 0:
            anchor = nodes[token_insertion_index]
            before_anchor = True
        elif token_insertion_index == len(node_locations):
            anchor = nodes[-1]
            before_anchor = False
        else:
            anchor = nodes[token_insertion_index - 1]
            before_anchor = False
        _LOG.debug('inserting %s %s %s', comment, 'before' if before_anchor else 'after', anchor)
        tree = insert_in_tree(tree, comment, anchor=anchor, before_anchor=before_anchor)
    _LOG.debug('tree after insertion:\n"""\n%s\n"""', typed_astunparse.dump(tree))
    # _LOG.warning('code after insertion:\n"""\n%s\n"""', typed_astunparse.unparse(tree).strip())
    return tree
