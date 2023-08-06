import ast
import linecache
import textwrap
from pathlib import Path
from traceback import FrameSummary

from tinyerr.anchor import Anchor
from tinyerr.config import Formatting


def get_offsets(frame: FrameSummary, line: str) -> tuple[int, int]:
    """
    Returns the offsets associated with the given frame and line (not lstripped)
    """
    start_offset = frame.colno + 1
    end_offset = frame.end_colno + 1
    if frame.lineno != frame.end_lineno:
        end_offset = len(line.rstrip())
    return start_offset, end_offset


def get_anchors(frame: FrameSummary) -> Anchor:
    """Returns the anchors associated with the given frame line"""
    line = linecache.getline(frame.filename, frame.lineno)
    start_offset, end_offset = get_offsets(frame, line)
    if frame.lineno == frame.end_lineno:
        return Anchor.from_segment(line, start_offset, end_offset)
    else:
        return Anchor.from_line(line, start_offset, end_offset)


def formatted_frame_code(frame: FrameSummary, indent: int = 4) -> str:
    """
    Returns the formatted code associated with this frame with anchors
    indicating the error location if necessary. For example::

        result = x + y
                 ~~^~~

    The indent parameter specifies how much the code should be indented
    """
    row = []
    if frame.line:
        row.append(frame.line.strip())
        if frame.colno is not None and frame.end_colno is not None:
            anchors = get_anchors(frame)
            row.append(str(anchors))

    return textwrap.indent("\n".join(row), prefix=" " * indent)


def _short_path(filename) -> Path:
    """
    Returns a relative path to the frame file if possible or an absolute path
    """
    try:
        return Path(filename).resolve().relative_to(Path.cwd())
    except ValueError:
        return Path(filename).resolve()


def frame_location(frame: FrameSummary) -> str:
    """
    Returns a readable string describing the location of the frame.
    Uses relative paths where possible
    """
    path = _short_path(frame.filename)
    return Formatting.frame_info.format(
        file=path, name=frame.name,
        lineno=frame.lineno, end_lineno=frame.end_lineno,
        colno=frame.colno, end_colno=frame.end_colno
    )


def format_frame(frame: FrameSummary) -> str:
    """
    Returns a formatted text block of the frame location and code line::

        File "<path>", line <line>, in <scope>

            <code line>

    """
    return "\n\n".join((
        frame_location(frame),
        formatted_frame_code(frame),
    ))


def frame_is_raise_statement(frame: FrameSummary) -> bool:
    lines = "".join(
        linecache.getline(frame.filename, i)
        for i in range(frame.lineno, frame.end_lineno + 1)
    )
    lines = textwrap.dedent(lines)
    try:
        tree = ast.parse(lines)
        match tree.body[0]:
            case ast.Raise():
                return True
    except SyntaxError:
        return False
    return False
