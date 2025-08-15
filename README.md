# Typer Shell!

Beautiful command-line shell with [Typer](https://github.com/tiangolo/typer)!

This is just an update to [click-shell](https://github.com/clarkperkins/click-shell) for typer.

I also added some features like:
- better help by default
- support for typer default functions (just name one of your commands 'default' and it will be triggered when nothing else is recognized)
- easily drop into an ipython terminal with the local context loaded with 'shell'
- each shell can have local parameters with helper functions for loading and saving them from files

[See it in action!](https://asciinema.org/a/xdYelspxaxpiJ9AhiekNLZtRI)

And checkout [the demo script](./demo.py):

To run the demos, you can execute them with `poetry run`:

```bash
poetry run python demo/demo.py
poetry run python demo/simple_demo.py
```

There are also sample helper functions in `typer_shell/samples.py` that you can use in your own applications.


```python
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
```

## Using Callbacks

Because `typer-shell` uses Typer's callback mechanism to launch the interactive shell, you cannot use the standard `@app.callback()` decorator, as it will conflict and prevent the shell from loading.

If you need to run code before the shell launches (for example, to set up state), you can pass a function to the `user_callback` parameter in `make_typer_shell`.

Your function will be called with the `Typer.Context` object before the shell starts.

```python
import typer
from typer_shell import make_typer_shell

def my_setup_logic(ctx: typer.Context):
    print("This runs before the shell starts!")
    # You can access and modify the context object here
    ctx.obj.my_value = 42

app = make_typer_shell(user_callback=my_setup_logic)

@app.command()
def my_command(ctx: typer.Context):
    print(f"my_value is: {ctx.obj.my_value}")

if __name__ == "__main__":
    app()
```
