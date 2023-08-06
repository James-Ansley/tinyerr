"""Dynamic global config objects."""


class ConfigMeta(type):
    def __setattr__(cls, key, value):
        if value is None:
            return
        else:
            super().__setattr__(key, value)


class Config(metaclass=ConfigMeta):
    def __init__(self):
        raise NotImplementedError("Cannot initialise instance of Config")


class Formatting(Config):
    frame_info = "{file}:{lineno} in {name}"
    code_indent = 4
    is_red = False


class ExecHandling(Config):
    traceback_limit = 0
    parent_context = None
    suppress_raise = True
