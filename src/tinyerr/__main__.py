import sys
from argparse import ArgumentParser

import tinyerr

parser = ArgumentParser(
    prog='TinyErr',
    description='Provides tiny errors that get straight to the point',
)

parser.add_argument('filename')
parser.add_argument('-tb', '--traceback', dest="traceback", type=int, default=0)

args = parser.parse_args()

tinyerr.activate(__file__, args.traceback)
with open(args.filename, 'r') as f:
    exec(compile(f.read(), args.filename, 'exec'))

sys.exit(0)
