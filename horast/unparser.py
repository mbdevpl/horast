"""Extension of typed_astunpare unparser for Python 3 that generates code with comments."""

import ast
import io
import logging

from astunparse.unparser import interleave
import typed_ast.ast3
import static_typing.unparser

from .nodes import Comment

_LOG = logging.getLogger(__name__)


def interleave_noncomment(inter, f, seq):
    """Call f on each item in seq, calling inter() in between."""
    seq = iter(seq)
    prev = None
    try:
        prev = next(seq)
        f(prev)
    except StopIteration:
        pass
    else:
        for x in seq:
            if not isinstance(prev, Comment):
                inter()
            f(x)
            prev = x


class Unparser(static_typing.unparser.Unparser):

    """Extension of static_typing.unparser.Unparser that handles Comment nodes."""

    def _List(self, t):
        self.write("[")
        interleave_noncomment(lambda: self.write(", "), self.dispatch, t.elts)
        self.write("]")

    def _Set(self, t):
        assert(t.elts)  # should be at least one element
        self.write("{")
        interleave_noncomment(lambda: self.write(", "), self.dispatch, t.elts)
        self.write("}")

    def _Dict(self, t):
        self.write("{")
        noncomment_keys = []
        comment_groups = []
        comment_group = []
        _LOG.info('keys  : %s', t.keys)
        _LOG.info('values: %s', t.values)
        for key in t.keys:
            if isinstance(key, Comment):
                comment_group.append(key)
                continue
            comment_groups.append(comment_group)
            comment_group = []
            noncomment_keys.append(key)
        noncomment_values = []
        comment_groups_iter = iter(comment_groups)
        try:
            comment_group = next(comment_groups_iter)
        except StopIteration:
            comment_group = None
        for value in t.values:
            if isinstance(value, Comment):
                comment_group.append(value)
                continue
            noncomment_values.append(value)
            try:
                comment_group = next(comment_groups_iter)
            except StopIteration:
                comment_group = None
        def write_triple(triple):
            (k, v, comments) = triple
            for comment in comments:
                self.dispatch(comment)
            self.dispatch(k)
            self.write(": ")
            self.dispatch(v)
        interleave(lambda: self.write(", "), write_triple, zip(
            noncomment_keys, noncomment_values, comment_groups))
        self.write("}")

    def _Tuple(self, t):
        self.write("(")
        if len(t.elts) == 1:
            (elt,) = t.elts
            self.dispatch(elt)
            self.write(",")
        else:
            interleave_noncomment(lambda: self.write(", "), self.dispatch, t.elts)
        self.write(")")

    def _Call(self, t):
        if isinstance(t, ast.Call):
            super()._Call(t)
            return

        self.dispatch(t.func)
        self.write("(")
        comma = False
        for e in t.args:
            if comma:
                self.write(", ")
            else:
                comma = True
            self.dispatch(e)
            if isinstance(e, Comment):
                comma = False
        for e in t.keywords:
            if comma:
                self.write(", ")
            else:
                comma = True
            self.dispatch(e)
            if isinstance(e, Comment):
                comma = False
        self.write(")")

    def _Comment(self, node):
        if node.eol:
            self.write('  #')
        else:
            self.fill('#')
        self.write(node.value.s)

    def _Directive(self, node):
        self.fill('#')
        self.write(node.value.s)


def unparse(tree: typed_ast.ast3.AST, *args, **kwargs) -> str:
    """Unparse AST based on typed_ast.ast3 with nodes as defined in horast.nodes into code."""
    assert isinstance(tree, typed_ast.ast3.AST), type(tree)
    stream = io.StringIO()
    Unparser(tree, *args, file=stream, **kwargs)
    return stream.getvalue()
