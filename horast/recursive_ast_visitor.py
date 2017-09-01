"""Recursive visitor of nodes in AST."""

import logging
import typing as t

import typed_ast.ast3

_LOG = logging.getLogger(__name__)


class RecursiveAstVisitor(typed_ast.ast3.NodeVisitor):
    """Perform a custom action on all nodes in a given AST."""

    def __init__(
            self, visitor: t.Callable[[typed_ast.ast3.AST], None], fields_first: bool = False,
            *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._node_visitor = visitor
        self._fields_first = fields_first

    def visit_fields(self, node: typed_ast.ast3.AST) -> None:
        """Visit all fields of a given node."""
        _LOG.debug('visiting all fields of node %s', node)
        assert hasattr(node, '_fields'), (type(node), node, type(node).__mro__)
        for field_name, field_value in typed_ast.ast3.iter_fields(node):
            _LOG.debug('visiting field %s of %s', field_name, node)
            if field_value is None \
                    or isinstance(field_value, (int, float, str, type, tuple)) \
                    or isinstance(type(field_value), t.TypingMeta):
                continue
            if isinstance(field_value, list):
                for field_value_elem in field_value:
                    self.visit(field_value_elem)
                continue
            self.visit(field_value)

    def generic_visit(self, node: typed_ast.ast3.AST) -> None:
        if self._fields_first:
            self.visit_fields(node)
            self._node_visitor(node)
        else:
            self._node_visitor(node)
            self.visit_fields(node)
