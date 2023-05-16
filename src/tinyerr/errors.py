import re
from pathlib import Path
from re import Pattern
from traceback import FrameSummary, StackSummary, extract_tb
from types import TracebackType
from typing import Self, Type, TypeVar

from tinyerr.frames import format_frame

Err = TypeVar("Err", bound=Exception)

COMMON_TYPE_NAMES = {
    "builtin_function_or_method": "function",
    "method-wrapper": "method",
}


def type_name(name):
    return COMMON_TYPE_NAMES.get(name, name)


class Error:
    type: Type[Exception] = Exception
    pattern: Pattern = re.compile(".")

    def __init__(
            self,
            exception: Err,
            stack: StackSummary,
            traceback_limit: int,
            context: Path | None = None
    ):
        self.exception = exception
        self.stack = stack
        self.traceback_limit = traceback_limit
        self.context = context

    @classmethod
    def from_exception(
            cls,
            exception: Exception,
            traceback: TracebackType,
            trabeback_limit,
            context: Path | None = None,
    ) -> Self:
        stack = extract_tb(traceback)
        for subtype in cls.__subclasses__():
            if (isinstance(exception, subtype.type)
                    and subtype.pattern.match(str(exception))):
                return subtype(exception, stack, trabeback_limit, context)
        return cls(exception, stack, trabeback_limit, context)

    def frames(self) -> StackSummary:
        if self.context is not None:
            idx = next(
                (i for i, frame in enumerate(self.stack)
                 if self.context.samefile(frame.filename)),
                -1
            )
            return self.stack[idx + 1:]
        return self.stack

    def formated_frames(self, limit: int = 1) -> str:
        return "\n\n".join(
            format_frame(frame) for frame in self.frames()[-limit:]
        )

    @property
    def groups(self) -> dict[str, str]:
        return self.pattern.match(str(self.exception)).groupdict()

    def message(self) -> str:
        return str(self.exception)

    def message_with_type(self) -> str:
        return f"{type(self.exception).__name__}: {self.message()}"

    def trace(self, limit: int = 1) -> str:
        trace = "\n\n".join((
            self.formated_frames(limit),
            self.message_with_type(),
        ))
        return f"\x1b[31m{trace}\x1b[0m"

    def __str__(self):
        return self.trace(self.traceback_limit)


class SyntaxErr(Error):
    type = SyntaxError
    pattern = re.compile(".*")

    def frames(self) -> StackSummary:
        start_line = self.exception.lineno
        end_line = self.exception.end_lineno
        start_col = self.exception.offset - 1
        end_col = self.exception.end_offset
        if start_line == end_line and end_col < start_col:
            end_col = start_col + 1
        return StackSummary.from_list([
            FrameSummary(
                self.exception.filename,
                start_line,
                name=self.stack[-1].name,
                end_lineno=end_line,
                colno=start_col,
                end_colno=end_col,
            )
        ])

    def message(self) -> str:
        return self.exception.msg


class IntValueError(Error):
    type = ValueError
    pattern = re.compile(
        r"invalid literal for int\(\) with base (?P<base>\d+): (?P<value>.*)"
    )

    def message(self) -> str:
        return (
            f"cannot convert {self.groups['value']} to int "
            f"(base {self.groups['base']})"
        )


class BoolOpTypeError(Error):
    type = TypeError
    pattern = re.compile(
        r"unsupported operand type\(s\) for (?P<op>.+): "
        r"'(?P<left>.*)' and '(?P<right>.*)'"
    )

    op_names = {
        "** or pow()": "**",
    }

    def op_name(self):
        return type(self).op_names.get(self.groups["op"], self.groups["op"])

    def message(self) -> str:
        return (
            f"cannot do "
            f"`<{type_name(self.groups['left'])}> "
            f"{self.op_name()} "
            f"<{type_name(self.groups['right'])}>`"
        )


class ConcatTypeError(Error):
    type = TypeError
    pattern = re.compile(
        r'can only concatenate .* \(not "(?P<right>.*)"\) to (?P<left>.*)'
    )

    def message(self) -> str:
        return (
            f"cannot do `<{type_name(self.groups['left'])}> "
            f"+ <{type_name(self.groups['right'])}>`"
        )


class NameErrorMessage(Error):
    type = NameError
    pattern = re.compile("name (?P<name>.*) is not defined")

    def message(self) -> str:
        return f"{self.groups['name']} is not defined"


class SubscriptableError(Error):
    type = TypeError
    pattern = re.compile("'(?P<type>.*)' object is not subscriptable")

    def message(self) -> str:
        # TODO – come up with something better
        return (
            f"cannot use square brackets on value of type "
            f"<{type_name(self.groups['type'])}>"
        )


class ListIndicesError(Error):
    type = TypeError
    pattern = re.compile(
        "(?P<container>.*) indices must be integers or slices, not (?P<type>.*)"
    )

    def message(self) -> str:
        return (
            f"cannot use <{type_name(self.groups['type'])}> "
            f"to index <{type_name(self.groups['container'])}>"
        )


class SliceError(Error):
    type = TypeError
    pattern = re.compile(
        "slice indices must be integers or None or have an __index__ method"
    )

    def message(self) -> str:
        # TODO – come up with something better
        # No type information is in the error or trace – making it difficult
        # to provide a nice error message. Misses __index__ as valid slice item
        return f"Slice indices must be of type <int> or left blank"
