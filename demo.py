#!/usr/bin/env python


from rich import print
from typer import Context

from typer_shell import make_typer_shell


class App:
    def __init__(self, name: str = "Bob"):
        self.name = name


app = make_typer_shell(prompt="🔥: ", obj=App(), params={"name": "Bob"}, params_path="params.yaml")
inner_app = make_typer_shell(prompt="🌲: ", params={"name": "Bob"}, params_path="innerparams.yaml")

app.add_typer(inner_app, name="inner")


@app.command()
# @inner_app.command()
def foobar(name: str = "Bob"):
    "Foobar command"
    print("Hello", name)


@app.command()
def name(ctx: Context, name: str = "Bob"):
    "Name command"
    print("Hello", name)


@app.command(hidden=True)
# @inner_app.command(hidden=True)
def default(ctx: Context, line: str = "Bob"):
    "Name command wrapper for default"
    ctx.invoke(name, ctx=ctx, name=line)


if __name__ == "__main__":
    app()
