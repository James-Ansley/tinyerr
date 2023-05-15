from typer import Typer

import tinyerr

app = Typer(add_completion=False)


@app.command()
def main(path: str):
    tinyerr.activate()
    namespace = dict(globals())
    if globals() is not locals():
        namespace.update(locals())
    with open(path, 'r') as infile:
        exec(compile(infile.read(), path, 'exec'), namespace)


app()
