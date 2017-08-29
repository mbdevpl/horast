"""Various helper functions to query and manipulate AST."""

import logging
import typing as t

import typed_ast.ast3

from .recursive_ast_visitor import RecursiveAstVisitor


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
    def accumulate_nodes(node):
        if not only_localizable or hasattr(node, 'lineno') and hasattr(node, 'col_offset'):
            nodes.append(node)
    visitor = RecursiveAstVisitor(accumulate_nodes, fields_first=True)
    visitor.visit(tree)
    return nodes


def get_ast_node_locations(nodes: t.List[typed_ast.ast3.AST]) -> t.List[t.Tuple[int, int]]:
    return [(
        node.lineno if hasattr(node, 'lineno') else None,
        node.col_offset if hasattr(node, 'col_offset') else None) for node in nodes]


def node_path_in_ast(
        tree: typed_ast.ast3.AST,
        target_node: typed_ast.ast3.AST) -> t.Optional[t.List[AstPathNode]]:
    """Find path to node in the given AST.

    Return a list of AstPathNode from root node up to the target node.

    Return None if node is not in the tree.
    """
    assert isinstance(tree, typed_ast.ast3.AST), type(tree)
    assert isinstance(target_node, typed_ast.ast3.AST), type(target_node)
    _LOG.debug('looking for node: %s', typed_ast.ast3.dump(target_node, include_attributes=True))
    nodes = []
    found = []
    def accumulate_nodes(node) -> None:
        if found:
            return
        nodes.append(node)
        _LOG.debug('node along the path %s', typed_ast.ast3.dump(node, include_attributes=True))
        if node is target_node:
            _LOG.debug('found target node')
            found.append(True)
    visitor = RecursiveAstVisitor(accumulate_nodes)
    visitor.visit(tree)
    if not found:
        return None
    root_node = nodes[0]
    node_path = [AstPathNode(target_node, None, None)]
    current_anchor = target_node
    reversed_anchor_index = 0
    reversed_nodes = list(reversed(list(enumerate(nodes))))
    while current_anchor is not root_node:
        reversed_anchor_index += 1
        for index, node in reversed_nodes[reversed_anchor_index:]:
            _LOG.debug('nodes[%i] is %s', index, node)
            for field_name, field_value in typed_ast.ast3.iter_fields(node):
                if field_value is None \
                        or isinstance(field_value, (int, float, str, type, tuple)) \
                        or isinstance(type(field_value), t.TypingMeta):
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
