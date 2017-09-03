"""Recursive transformer of nodes in AST."""

import logging
import typing as t

import typed_ast.ast3

_LOG = logging.getLogger(__name__)


class RecursiveAstTransformer(typed_ast.ast3.NodeTransformer):
    """Recurisvely overwrite all nodes in a given AST."""

    def __init__(
            self, transformer: t.Callable[[typed_ast.ast3.AST], typed_ast.ast3.AST],
            fields_first: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._node_transformer = transformer
        self._fields_first = fields_first

    def transform_fields(self, node: typed_ast.ast3.AST) -> None:
        """Transform all fields of a given node."""
        _LOG.debug('transforming all fields of node %s', node)
        assert hasattr(node, '_fields'), (type(node), node, type(node).__mro__)
        for field_name, field_value in typed_ast.ast3.iter_fields(node):
            _LOG.debug('transforming field %s of %s', field_name, node)
            if field_value is None \
                    or isinstance(field_value, (int, float, str, type, tuple)) \
                    or isinstance(type(field_value), t.TypingMeta):
                continue
            if isinstance(field_value, list):
                for i, field_value_elem in enumerate(field_value):
                    field_value[i] = self.visit(field_value_elem)
                continue
            setattr(node, field_name, self.visit(field_value))

    def generic_visit(self, node: typed_ast.ast3.AST) -> typed_ast.ast3.AST:
        if self._fields_first:
            self.transform_fields(node)
            return self._node_transformer(node)
        node = self._node_transformer(node)
        self.transform_fields(node)
        return node
