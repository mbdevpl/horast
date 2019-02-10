"""Various helper functions to query and manipulate AST."""

import ast
import logging
import re
import typing as t

import asttokens
from static_typing.ast_manipulation import RecursiveAstVisitor
import typed_ast.ast3

from .token_tools import Scope

_LOG = logging.getLogger(__name__)

AstPathNode = t.NamedTuple('AstPathNode', [
    ('node', typed_ast.ast3.AST), ('field', t.Optional[str]), ('index', t.Optional[int])])
"""Node on a AST path.

Meaning of fields:
- node is an AST node on the path
- field is name of the field in that node; None if node is the final (i.e. target) node of the path
- index is index of the next node in the field if value of the field is a list, None otherwise
"""


def ast_to_list(
        tree: typed_ast.ast3.AST, only_localizable: bool = False) -> t.List[typed_ast.ast3.AST]:
    """Generate a flat list of nodes in AST."""
    nodes = []

    class Visitor(RecursiveAstVisitor[typed_ast.ast3]):
        def visit_node(self, node):
            if not only_localizable or hasattr(node, 'lineno') and hasattr(node, 'col_offset'):
                nodes.append(node)
    visitor = Visitor()
    visitor.visit(tree)
    return nodes


def get_ast_node_locations(nodes: t.List[typed_ast.ast3.AST]) -> t.List[t.Tuple[int, int]]:
    return [(
        node.lineno if hasattr(node, 'lineno') else None,
        node.col_offset if hasattr(node, 'col_offset') else None) for node in nodes]


def convert_1d_str_index_to_2d(
        text: str, index: int, line_separator: str = '\n',
        newline_starts: t.List[int] = None) -> t.Tuple[int, int]:
    """Convert 1D index in text to tuple (lineno, col_offset)."""
    assert isinstance(text, str), type(text)
    assert isinstance(index, int), type(index)
    if newline_starts is None:
        newline_starts = [m.end() for m in re.finditer(line_separator, text)]
    if index < 0 or index > len(text):
        raise ValueError('index={} is outside [0,{}]'.format(index, len(text)))
    lineno = 1
    for newline_start in newline_starts:
        if newline_start > index:
            break
        lineno += 1
    col_offset = index
    if newline_starts and lineno > 1:
        col_offset -= newline_starts[lineno - 2]
    _LOG.debug('converted %s[%i] into (%i, %i)', repr(text), index, lineno, col_offset)
    return lineno, col_offset


def get_ast_node_scopes(code: str, nodes: t.List[typed_ast.ast3.AST]) -> t.List[Scope]:
    atok = asttokens.ASTTokens(code, tree=ast.parse(code))
    ast_nodes = ast_to_list(atok.tree)
    assert len(ast_nodes) == len(nodes), (len(ast_nodes), len(nodes))
    newline_starts = [m.end() for m in re.finditer('\n', code)]
    _LOG.debug('new lines in code: %s', newline_starts)
    scopes = []
    _LOG.debug('marked %i nodes:', len(ast_nodes))
    for node in ast_nodes:
        raw_node_scope = atok.get_text_range(node)
        _LOG.debug(
            'node %s at %s: code="""%s""", tree=%s',
            type(node).__name__, raw_node_scope, atok.get_text(node), ast.dump(node))
        node_scope = Scope(*[
            convert_1d_str_index_to_2d(code, _, newline_starts=newline_starts)
            for _ in raw_node_scope])
        _LOG.debug('scope %s is %s', raw_node_scope, node_scope)
        scopes.append(node_scope)
    return scopes


def node_path_in_ast(
        tree: typed_ast.ast3.AST,
        target_node: typed_ast.ast3.AST) -> t.List[AstPathNode]:
    """Find path to node in the given AST.

    Return a list of AstPathNode from root node up to the target node.
    """
    assert isinstance(tree, typed_ast.ast3.AST), type(tree)
    assert isinstance(target_node, typed_ast.ast3.AST), type(target_node)
    _LOG.debug('looking for node: %s', typed_ast.ast3.dump(target_node, include_attributes=True))
    nodes = ast_to_list(tree)
    nodes = nodes[:nodes.index(target_node) + 1]
    node_path = [AstPathNode(target_node, None, None)]
    current_anchor = target_node
    reversed_anchor_index = 0
    reversed_nodes = list(reversed(list(enumerate(nodes))))
    while current_anchor is not nodes[0]:
        reversed_anchor_index += 1
        for index, node in reversed_nodes[reversed_anchor_index:]:
            _LOG.debug('nodes[%i] is %s', index, node)
            for field_name, field_value in typed_ast.ast3.iter_fields(node):
                if field_value is None or isinstance(field_value, (int, float, str, type, tuple)):
                    continue
                if isinstance(field_value, list):
                    found = False
                    for i, field_value_elem in enumerate(field_value):
                        if field_value_elem is current_anchor:
                            current_anchor = node
                            reversed_anchor_index += index
                            node_path.append(AstPathNode(node, field_name, i))
                            found = True
                            _LOG.debug('"%s[%i]" of %s is on the path', field_name, i, node)
                            break
                    if found:
                        break
                    continue
                if field_value is current_anchor:
                    current_anchor = node
                    reversed_anchor_index += index
                    node_path.append(AstPathNode(node, field_name, None))
                    _LOG.debug('"%s" of %s is on the path', field_name, node)
                    break
    return list(reversed(node_path))


def find_in_ast(
        code: str, tree: typed_ast.ast3.AST, nodes: t.List[typed_ast.ast3.AST],
        scope: Scope) -> t.Tuple[t.List[AstPathNode], bool]:
    """Return tuple: (path, before).

    Where:
    - path is path to the anchor node for the target scope
    - before is boolean flag set to True if target scope is before the anchor node, False otherwise
    """
    scopes = get_ast_node_scopes(code, nodes)
    assert len(nodes) == len(scopes), (len(nodes), len(scopes))
    node_scopes_by_start = list(zip(nodes, scopes))
    node_scopes_by_start.sort(key=lambda _: _[1].end, reverse=True)
    node_scopes_by_start.sort(key=lambda _: _[1].start)
    _LOG.debug('by start: %s', node_scopes_by_start)
    node_scopes_by_end = list(zip(nodes, scopes))
    node_scopes_by_end.sort(key=lambda _: _[1].start, reverse=True)
    node_scopes_by_end.sort(key=lambda _: _[1].end)
    _LOG.debug('by end: %s', node_scopes_by_end)
    target_scope = scope
    _LOG.debug('the target scope %s', target_scope)

    node_by_end_after_index = None
    for i, (node, scope_) in enumerate(node_scopes_by_end):
        if target_scope.start > scope_.end:
            node_by_end_after_index = i
            _LOG.debug('is after node %s at %s', node, scope_)
            break
    if node_by_end_after_index is None:
        _LOG.debug('is not after any node')

    node_by_start_before_index = None
    for i, (node, scope_) in enumerate(node_scopes_by_start):
        if target_scope.end < scope_.start:
            node_by_start_before_index = i
            _LOG.debug('is before node %s at %s', node, scope_)
            break
    if node_by_start_before_index is None:
        _LOG.debug('is not before any node')

    scopes_containing_target_scope = []
    for i, (node, scope_) in enumerate(node_scopes_by_start):
        if scope_.start > target_scope.start:
            break
        if scope_.end > target_scope.end:
            scopes_containing_target_scope.append((node, scope_))
    _LOG.debug('is within nodes %s', scopes_containing_target_scope)

    if node_by_end_after_index is None:
        _LOG.debug('target %s is before first node', target_scope)
        assert isinstance(nodes[0], (typed_ast.ast3.Module, typed_ast.ast3.Interactive)), \
            type(nodes[0])
        return ([AstPathNode(nodes[0], 'body', 0)], True)

    if node_by_start_before_index is None and not scopes_containing_target_scope:
        _LOG.debug('target %s is after last node', target_scope)
        assert isinstance(nodes[0], (typed_ast.ast3.Module, typed_ast.ast3.Interactive)), \
            type(nodes[0])
        assert len(nodes[0].body) > 0
        return ([AstPathNode(nodes[0], 'body', len(nodes[0].body) - 1)], False)
    elif node_by_start_before_index is None or not scopes_containing_target_scope:
        raise NotImplementedError(
            'inconsistent results for target {} in:\n"""\n{}\nafter {}, before {}, within {}"""'
            .format(target_scope, code, node_by_end_after_index, node_by_start_before_index,
                    scopes_containing_target_scope))

    assert node_by_end_after_index is not None
    assert node_by_start_before_index is not None
    assert scopes_containing_target_scope
    _LOG.debug(
        'target %s is neither before first node nor after last node in:\n"""\n%s\n"""'
        '\nbut between %s and %s, within %s',
        target_scope, code, node_scopes_by_end[node_by_end_after_index],
        node_scopes_by_start[node_by_start_before_index], scopes_containing_target_scope)
    within_node, _ = scopes_containing_target_scope[-1]
    before_node, _ = node_scopes_by_start[node_by_start_before_index]
    path = node_path_in_ast(tree, before_node)
    assert len(path) >= 2, path
    assert path[-2].node is within_node, (path[-2].node, within_node)
    return (path[:-1], True)


def insert_at_path_in_tree(
        tree: typed_ast.ast3.AST, inserted: typed_ast.ast3.AST,
        path_to_anchor: t.Sequence[AstPathNode],
        before_anchor: bool = False) -> typed_ast.ast3.AST:
    """Insert a new AST node into an existing AST at exactly specified location."""
    assert isinstance(tree, typed_ast.ast3.AST), type(tree)
    assert isinstance(inserted, typed_ast.ast3.AST), type(inserted)
    # assert isinstance(anchor, typed_ast.ast3.AST), type(anchor)
    parent, field, index = path_to_anchor[-1]
    if not before_anchor:
        index += 1
    getattr(parent, field).insert(index, inserted)
    return tree


def insert_in_tree(
        tree: typed_ast.ast3.AST, inserted: typed_ast.ast3.AST, anchor: typed_ast.ast3.AST,
        before_anchor: bool = False, strict: bool = False) -> typed_ast.ast3.AST:
    """Insert a new AST node into an existing AST near the anchor node.

    Try to maintain correctness after insertion.
    """
    assert isinstance(tree, typed_ast.ast3.AST), type(tree)
    assert isinstance(inserted, typed_ast.ast3.AST), type(inserted)
    assert isinstance(anchor, typed_ast.ast3.AST), type(anchor)
    node_path = node_path_in_ast(tree, anchor)
    if node_path is None:
        raise ValueError('the anchor node {} not found in AST {}'.format(anchor, tree))
    _LOG.debug('node path: %s', node_path)
    try:
        parent, field, index = node_path[-2]
    except IndexError as err:
        if strict:
            raise NotImplementedError('cannot insert at AST root') from err
        parent, field, index = node_path[0].node, 'body', 0
    _LOG.debug('parent of anchor node: %s', parent)
    if strict and index is None:
        raise NotImplementedError('cannot insert into a non-list field')
    node_path_index = -2
    if field == 'targets':
        index = None  # don't insert anything into assignment
    while index is None:
        node_path_index -= 1
        parent, field, index = node_path[node_path_index]
        if field == 'targets':
            index = None  # don't insert anything into assignment
    if before_anchor:
        pass
    else:
        index += 1
    getattr(parent, field).insert(index, inserted)
    return tree
