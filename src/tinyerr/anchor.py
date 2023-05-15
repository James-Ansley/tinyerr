import ast
from dataclasses import dataclass
from typing import Self

__all__ = ["Anchor"]


@dataclass
class Anchor:
    """Anchor points for indicating ranges of text."""
    start: int
    end: int
    outer_start: int | None = None
    outer_end: int | None = None
    primary_char: str = "^"
    secondary_char: str = "~"

    def __post_init__(self):
        if self.outer_start is None:
            self.outer_start = self.start
        if self.outer_end is None:
            self.outer_end = self.end

    @classmethod
    def from_segment(cls, line: str, start: int, end: int) -> Self:
        """
        Returns an Anchor with offsets relative to the first non-whitespace char
        """
        try:
            segment = line[start - 1: end - 1]
            start_inner, end_inner = primary_anchors_from_segment(segment)
            start_inner += start
            end_inner += start
        except Exception:
            start_inner, end_inner = start, end
        offset = len(line) - len(line.lstrip())
        return cls(
            start_inner - offset,
            end_inner - offset,
            start - offset,
            end - offset,
        )

    @classmethod
    def from_line(cls, line: str, start: int, end: int) -> Self:
        """
        Returns an Anchor with offsets relative to the first non-whitespace char
        """
        offset = len(line) - len(line.lstrip())
        return cls(start - offset, end - offset)

    def __len__(self):
        return self.outer_end - self.outer_start

    def __str__(self):
        return "".join((
            " " * (self.outer_start - 1),
            self.secondary_char * (self.start - self.outer_start),
            self.primary_char * (self.end - self.start),
            self.secondary_char * (self.outer_end - self.end),
        ))


def primary_anchors_from_segment(segment):
    """
    Returns the specific location of interesting operators etc.
    """
    tree = ast.parse(segment)
    match tree.body[0]:
        case ast.Expr(ast.BinOp() as expr):
            return binop_primary_anchors(expr, segment)
        case ast.Expr(ast.Subscript() as expr):
            return subscript_primary_anchors(expr)


def binop_primary_anchors(expr: ast.BinOp, segment) -> tuple[int, int]:
    """
    Returns the operator location for binary ops::

        x + y
          ^
    """
    operator_start = expr.left.end_col_offset
    operator_end = expr.right.col_offset

    operator_str = segment[operator_start:operator_end]
    operator_offset = len(operator_str) - len(operator_str.lstrip())

    left_anchor = expr.left.end_col_offset + operator_offset
    right_anchor = left_anchor + len(operator_str.strip())
    return left_anchor, right_anchor


def subscript_primary_anchors(expr: ast.Subscript) -> tuple[int, int]:
    """
    Returns the start and end indices of the subscript::

        value[1:2]
             ^   ^
    """
    return (
        expr.value.end_col_offset,
        expr.slice.end_col_offset + 1,
    )
