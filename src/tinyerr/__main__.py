import sys
from argparse import ArgumentParser
from pathlib import Path

import tinyerr
from tinyerr.config import ExecHandling, Formatting

parser = ArgumentParser(
    prog="TinyErr",
    description="Provides tiny errors that get straight to the point",
)

parser.add_argument("filename")

parser.add_argument(
    "-tb", "--traceback", type=int, default=0,
    help="The traceback limit (0 for no limit)"
)
parser.add_argument(
    "--suppress-raise", action="store_true",
    help="Prevents frames that only contain `Raise` statements from being "
         "shown in stack trace"
)

parser.add_argument(
    "-r", "--red", dest="is_red", action="store_true",
    help="Whether to wrap the output in red ANSI escape codes"
)
parser.add_argument(
    "-f", "--format",
    help="A format string to specify how frame info should be displayed. "
         "Has the following named params available: file, name, lineno, "
         "end_lineno, colno, end_colno. "
         "Default is \"{file}:{lineno} in {name}\""
)

args = parser.parse_args()

Formatting.is_red = args.is_red
Formatting.frame_info = args.format

ExecHandling.parent_context = Path(__file__)
ExecHandling.traceback_limit = args.traceback
ExecHandling.suppress_raise = args.suppress_raise

tinyerr.activate()
with open(args.filename, "r") as f:
    exec(compile(f.read(), args.filename, "exec"), {'__name__': '__main__'})

sys.exit(0)
