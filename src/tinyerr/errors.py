import re
from re import Pattern
from traceback import FrameSummary, StackSummary, extract_tb
from types import TracebackType
from typing import Self, Type, TypeVar

from tinyerr.config import ExecHandling
from tinyerr.frames import format_frame, frame_is_raise_statement

Err = TypeVar("Err", bound=BaseException)

COMMON_TYPE_NAMES = {
    "builtin_function_or_method": "function",
    "method-wrapper": "method",
}


def type_name(name):
    return COMMON_TYPE_NAMES.get(name, name)


class Error:
    type: Type[Exception] = Exception
    pattern: Pattern = re.compile(".")

    def __init__(self, exception: Err, stack: StackSummary):
        self.exception = exception
        self.stack = stack

        context = exception.__context__
        suppress_context = exception.__suppress_context__
        cause = exception.__cause__

        self.context = None
        if context is not None and not suppress_context:
            self.context = Error.from_exception(context, context.__traceback__)

        self.cause = None
        if cause is not None:
            self.cause = Error.from_exception(cause, cause.__traceback__)

    @classmethod
    def from_exception(cls, exception: Err, traceback: TracebackType) -> Self:
        stack = extract_tb(traceback)
        for subtype in cls.__subclasses__():
            if (isinstance(exception, subtype.type)
                    and subtype.pattern.match(str(exception))):
                return subtype(exception, stack)
        return cls(exception, stack)

    def frames(self) -> StackSummary:
        frames = self.stack
        if ExecHandling.suppress_raise:
            frames = StackSummary.from_list(
                [f for f in frames if not frame_is_raise_statement(f)]
            )
        if ExecHandling.parent_context is not None:
            idx = next(
                (i for i, frame in enumerate(self.stack)
                 if ExecHandling.parent_context.samefile(frame.filename)),
                -1
            )
            return frames[idx + 1:]
        return frames

    def formatted_frames(self, limit: int = 1) -> str:
        return "\n\n".join(
            format_frame(frame) for frame in self.frames()[-limit:]
        )

    @property
    def groups(self) -> dict[str, str]:
        return self.pattern.match(str(self.exception)).groupdict()

    def message(self) -> str:
        return str(self.exception)

    def message_with_type(self) -> str:
        message = self.message()
        if not message:
            return f"{type(self.exception).__name__}"
        return f"{type(self.exception).__name__}: {self.message()}"

    def trace(self, limit: int = 0) -> str:
        # TODO – Do this a better way
        result = []
        if self.cause is not None:
            result.append(self.cause.trace(limit))
            result.append("The above exception caused the following:")
        if self.context is not None:
            result.append(self.context.trace(limit))
            result.append(
                "The following occurred while handling the above exception:"
            )
        result.append(self.formatted_frames(limit))
        result.append(self.message_with_type())
        return "\n\n".join(r for r in result if r)

    def __str__(self):
        return self.trace(ExecHandling.traceback_limit)


class SyntaxErr(Error):
    type = SyntaxError
    pattern = re.compile(".*")

    def frames(self) -> StackSummary:
        start_line = self.exception.lineno
        end_line = self.exception.end_lineno
        start_col = self.exception.offset - 1
        end_col = self.exception.end_offset
        if start_line == end_line and end_col <= start_col:
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


class IntTypeError(Error):
    type = TypeError
    pattern = re.compile(
        r"int\(\) argument must be a string, "
        r"a bytes-like object or a real number, not '(?P<type>.*)'"
    )

    def message(self) -> str:
        return f"cannot convert <{type_name(self.groups['type'])}> to int"


class FloatTypeError(Error):
    type = TypeError
    pattern = re.compile(
        r"float\(\) argument must be a string or a real number, "
        r"not '(?P<type>.*)'"
    )

    def message(self) -> str:
        return f"cannot convert <{type_name(self.groups['type'])}> to float"


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
            f"cannot use square brackets with values of type "
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


class ImportNameError(Error):
    type = ImportError
    pattern = re.compile(
        "cannot import name '(?P<name>.*)' from '(?P<module>.*)' .*"
    )

    def message(self) -> str:
        return (
            f"`{self.groups['name']}` not found in "
            f"module `{self.groups['module']}`"
        )
