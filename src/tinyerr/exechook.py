import sys
from pathlib import Path
from types import TracebackType
from typing import Type

from tinyerr.errors import Error
from tinyerr.trace import save_traceback

PARENT_CONTEXT: Path | None = None


def activate(file: str | None = None):
    """
    Changes sys.excepthook to use TinyErr exception handling

    The file parameter specifies a "cutoff" file for frames in traceback
    stacks. Any frames above and including the first frame whose file
    location is the given parameter file will not be included in TinyErr
    tracebacks. This is useful when using tinyerr to run other user given code.
    """
    global PARENT_CONTEXT
    if file is not None:
        PARENT_CONTEXT = Path(file)
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
    err = Error.from_exception(except_value, tracebac, PARENT_CONTEXT)
    print(err, file=sys.stderr)
    save_traceback(err)
