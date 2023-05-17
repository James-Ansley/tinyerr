# TinyErr

TinyErr (pronounced tinier) provides tiny errors that get straight to the point.

> Project is still in early Alpha – significant changes are expected and
> features are limited

## Install

```
pip install tinyerr
```

> While TinyErr is in alpha, it may be best to install directly from GitHub for
> the latest changes:
> ```
> pip install git+https://github.com/James-Ansley/tinyerr.git
> ```

## Example

`main.py`:

```python
def foo(x, y):
    return bar(x, y)


def bar(x, y):
    return x + y


result = foo(5, "Hello")
print(result)
```

Running `tinyerr main.py` produces:

```text
File "main.py", line 9, in <module>

    result = foo(5, "Hello")
             ^^^^^^^^^^^^^^^

File "main.py", line 2, in foo

    return bar(x, y)
           ^^^^^^^^^

File "main.py", line 6, in bar

    return x + y
           ~~^~~

TypeError: cannot do `<int> + <str>`
```

By default, the traceback limit is set to 0 (the entire stack). This can be
configured with the `-tb` or `--traceback` command line option.
e.g. `tinyerr -tb 1 main.py` will yield:

```text
File "main.py", line 6, in bar

    return x + y
           ~~^~~

TypeError: cannot do `<int> + <str>`
```
