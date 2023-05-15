import abc
import re
from re import Match, Pattern
from typing import Type


class ErrorMessage(abc.ABC):
    type: Type[Exception] = NotImplemented
    pattern: Pattern = NotImplemented

    def __init__(self, match: Match):
        self.match = match

    @classmethod
    def from_error(cls, value: Exception) -> str:
        """
        Returns a concise error message if one is known otherwise the
        original error message from value.
        """
        str_val = str(value)
        for exception in cls.__subclasses__():
            if (
                    isinstance(value, exception.type)
                    and (m := exception.pattern.match(str_val))
            ):
                return str(exception(m))
        return str_val

    @property
    def groups(self) -> dict[str, str]:
        return self.match.groupdict()


class IntValueError(ErrorMessage):
    type = ValueError
    pattern = re.compile(
        r"invalid literal for int\(\) with base (?P<base>\d+): (?P<value>.*)"
    )

    def __str__(self):
        return (
            f"Cannot convert {self.groups['value']} to int "
            f"(base {self.groups['base']})"
        )


class BoolOpTypeError(ErrorMessage):
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

    def __str__(self):
        return (
            f"Cannot do "
            f"`<{self.groups['left']}> "
            f"{self.op_name()} "
            f"<{self.groups['right']}>`"
        )


class ConcatTypeError(ErrorMessage):
    type = TypeError
    pattern = re.compile(
        r'can only concatenate .* \(not "(?P<right>.*)"\) to (?P<left>.*)'
    )

    def __str__(self):
        return (
            f"Cannot do "
            f"`<{self.groups['left']}> + <{self.groups['right']}>`"
        )


class NameErrorMessage(ErrorMessage):
    type = NameError
    pattern = re.compile("name (?P<name>.*) is not defined")

    def __str__(self):
        return f"{self.groups['name']} is not defined"
