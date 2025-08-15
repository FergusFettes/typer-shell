#!/usr/bin/env python
from typer_shell import make_typer_shell

app = make_typer_shell(prompt="simple: ")

@app.command()
def hello(name: str):
    """
    Say hello to someone.
    """
    print(f"Hello {name}")

if __name__ == "__main__":
    app()
