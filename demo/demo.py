#!/usr/bin/env python
from pathlib import Path

from rich import print
from typer import Context

from typer_shell import make_typer_shell
from typer_shell.samples import add_sample_commands

class App:
    def __init__(self, name: str = "Bob"):
        self.name = name

def on_finished(_):
    print('Done! And here is your goodbye message.')

def user_callback(ctx: Context):
    print("This is a user callback!")

app = make_typer_shell(prompt="🔥: ", on_finished=on_finished, obj=App(), user_callback=user_callback)
add_sample_commands(app)

inner_app = make_typer_shell(prompt="🌲: ", on_finished=on_finished)
add_sample_commands(inner_app)

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

# Set both the shell and the inner shell to have the same default
@app.command(hidden=True)
@inner_app.command(hidden=True)
def default(ctx: Context, line: str = "Bob"):
    "Name command wrapper for default"
    ctx.invoke(name, ctx=ctx, name=line)

if __name__ == "__main__":
    app()