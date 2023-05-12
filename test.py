#!/usr/bin/env python


from rich import print
from typer import Typer

from typer_shell import make_typer_shell

app: Typer = Typer()
make_typer_shell(app, prompt="🔥: ")
subapp: Typer = Typer()

default = lambda x: print(f"Inner Default, args: {x}")

make_typer_shell(
    subapp,
    prompt="🌲: ",
    intro="\n Welcome to the inner shell! Type help to see commands.\n",
    default=default
)
app.add_typer(subapp, name="inner")
app.aliases.update({"i": "inner"})


@app.command()
def foobar(hello: str = "world"):
    "Foobar command"
    print("foobar with hello: ", hello)


app.aliases.update({"f": "foobar"})


@subapp.command(name="foobar")
def _foobar():
    "Foobar command"
    print("foobar")


if __name__ == "__main__":
    app()
