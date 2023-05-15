import sys
import traceback
from pathlib import Path
from types import TracebackType
from typing import Type

from tinyerr.errors import ErrorMessage
from tinyerr.frames import format_frame_summary


def activate():
    sys.excepthook = excepthook


def deactivate():
    sys.excepthook = sys.__excepthook__


def _short_path(filename):
    try:
        return Path(filename).resolve().relative_to(Path.cwd())
    except ValueError:
        return Path(filename).resolve()


def excepthook(
        exec_type: Type[Exception], value: Exception, tracebac: TracebackType
):
    frame = traceback.extract_tb(tracebac)[-1]
    message = "\n".join((
        f"File \"{_short_path(frame.filename)}\", line {frame.lineno}",
        "",
        format_frame_summary(frame),
        "",
        f"{exec_type.__name__}: {ErrorMessage.from_error(value)}",
    ))
    print(message, file=sys.stderr)
