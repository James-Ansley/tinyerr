import pickle
from pathlib import Path

from tinyerr.errors import Error

TRACEBACK_STORE = (Path(__file__) / ".." / "last_traceback").resolve()


def save_traceback(error: Error):
    with open(TRACEBACK_STORE, "wb") as f:
        pickle.dump(error, f)


def last_traceback():
    try:
        with open(TRACEBACK_STORE, "rb") as f:
            error: Error = pickle.load(f)
        return error.trace(0)
    except FileNotFoundError:
        return "No trace was found"
    except pickle.UnpicklingError:
        return "Error loading trace"
