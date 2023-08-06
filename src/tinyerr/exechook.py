import sys
from types import TracebackType
from typing import Type

from tinyerr.config import Formatting
from tinyerr.errors import Error


def activate():
    """
    Changes sys.excepthook to use TinyErr exception handling

    The file parameter specifies a "cutoff" file for frames in traceback
    stacks. Any frames above and including the first frame whose file
    location is the given parameter file will not be included in TinyErr
    tracebacks. This is useful when using tinyerr to run other user given code.
    """
    sys.excepthook = excepthook


def deactivate():
    """Reverts sys.excepthook to the Python default"""
    sys.excepthook = sys.__excepthook__


def excepthook(
        except_type: Type[Exception],
        except_value: Exception,
        tracebac: TracebackType,
):
    """TinyErrs custom excepthook"""
    err = Error.from_exception(except_value, tracebac)
    err = red(str(err)) if Formatting.is_red else str(err)
    print(err, file=sys.stderr)


def red(msg: str) -> str:
    return f"\x1b[31m{msg}\x1b[0m"
