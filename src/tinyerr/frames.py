import linecache
import textwrap
from traceback import FrameSummary

from tinyerr.anchor import Anchor


def get_offsets(frame: FrameSummary, line: str) -> tuple[int, int]:
    start_offset = normalise(line, frame.colno) + 1
    end_offset = normalise(line, frame.end_colno) + 1
    if frame.lineno != frame.end_lineno:
        end_offset = len(line.rstrip())
    return start_offset, end_offset


def get_anchors(frame: FrameSummary, line: str) -> Anchor:
    start_offset, end_offset = get_offsets(frame, line)
    if frame.lineno == frame.end_lineno:
        return Anchor.from_segment(line, start_offset, end_offset)
    else:
        return Anchor.from_line(line, start_offset, end_offset)


def format_frame_summary(frame: FrameSummary):
    indent = 4
    row = []
    if frame.line:
        row.append(frame.line.strip())
        if frame.colno is not None and frame.end_colno is not None:
            original_line = linecache.getline(frame.filename, frame.lineno)
            anchors = get_anchors(frame, original_line)
            if len(anchors) <= len(original_line.strip()):
                row.append(str(anchors))

    return textwrap.indent("\n".join(row), prefix=" " * indent)


def normalise(line, offset):
    as_utf8 = line.encode('utf-8')
    return len(as_utf8[:offset].decode("utf-8", errors="replace"))
