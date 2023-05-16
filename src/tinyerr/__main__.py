import sys

import tinyerr
from tinyerr.trace import last_traceback

_, path = sys.argv

if path == "trace":
    print(last_traceback(), file=sys.stderr)
else:
    tinyerr.activate(__file__)
    with open(path, 'r') as f:
        exec(compile(f.read(), path, 'exec'))

sys.exit(0)
