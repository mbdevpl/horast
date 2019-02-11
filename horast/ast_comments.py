"""Extract comments from untouched source code and insert them into the AST."""

import logging
import tokenize
import typing as t

import typed_ast.ast3
import typed_astunparse

from .nodes import Comment
from .token_tools import get_token_locations, get_token_scopes
from .ast_tools import \
    ast_to_list, get_ast_node_locations, find_in_ast, insert_at_path_in_tree, insert_in_tree

_LOG = logging.getLogger(__name__)


def insert_comment_tokens(
        code: str, tree: typed_ast.ast3.AST,
        comment_tokens: t.List[tokenize.TokenInfo]) -> typed_ast.ast3.AST:
    """Insert comment tokens into an AST obtained from typed_ast parser."""
    assert isinstance(tree, typed_ast.ast3.AST)
    assert isinstance(comment_tokens, list)
    nodes = ast_to_list(tree)
    scopes = get_token_scopes(comment_tokens)
    for comment_token, scope in zip(comment_tokens, scopes):
        path_to_anchor, before_anchor = find_in_ast(code, tree, nodes, scope)
        if before_anchor:
            eol = False
        else:
            assert path_to_anchor
            anchor = path_to_anchor[-1]
            assert isinstance(anchor.field, str), type(anchor.field)
            node = getattr(anchor.node, anchor.field)
            if anchor.index is not None:
                node = node[anchor.index]
            assert hasattr(node, 'lineno'), typed_ast.ast3.dump(node, include_attributes=True)
            eol = node.lineno == scope.start[0] and node.lineno == scope.end[0]
        comment = Comment.from_token(comment_token, eol=eol)
        _LOG.debug('inserting %s %s %s', comment, 'before' if before_anchor else 'after',
                   path_to_anchor[-1])
        tree = insert_at_path_in_tree(tree, comment, path_to_anchor, before_anchor)
    return tree


def insert_comment_tokens_approx(
        tree: typed_ast.ast3.AST, tokens: t.List[tokenize.TokenInfo]) -> typed_ast.ast3.AST:
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
        comment = Comment.from_token(token, eol)
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
