#!/usr/bin/env python


from rich import print
from typer import Typer, Context

from typer_shell import make_typer_shell


app = make_typer_shell(prompt="🔥: ", default="name_wrapper")
inner_app = make_typer_shell(prompt="🌲: ", default="foobar")

app.add_typer(inner_app, name="inner")


@app.command()
@inner_app.command()
def foobar(name: str = "Bob"):
    "Foobar command"
    print("Hello", name)


@app.command()
def name(ctx: Context, name: str = "Bob"):
    "Name command"
    print("Hello", name)


@app.command(hidden=True)
def name_wrapper(ctx: Context, line: str = "Bob"):
    "Name command wrapper for default"
    ctx.invoke(name, ctx=ctx, name=line)


if __name__ == "__main__":
    app()
