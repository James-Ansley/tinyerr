# TinyErr

TinyErr (pronounced tinier) provides tiny errors that get straight to the point.

> Project is still in early Alpha – significant changes are expected and
> features are limited

## Install

```
pip install tinyerr
```

## Example

```python
# main.py:
result = 3.0 + {}
```

Running `tinyerr main.py` produces:

```text
File "main.py", line 1

    result = 3.0 + {}
             ~~~~^~~~

TypeError: Cannot do `<float> + <dict>`
```
