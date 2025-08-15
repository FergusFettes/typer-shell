# Typer Shell!

Beautiful command-line shell with [Typer](https://github.com/tiangolo/typer)!

This is just an update to [click-shell](https://github.com/clarkperkins/click-shell) for typer.

I also added some features like:
- better help by default
- support for typer default functions (just name one of your commands 'default' and it will be triggered when nothing else is recognized)
- easily drop into an ipython terminal with the local context loaded with 'shell'
- rich sample commands for file operations, tables, progress bars, and more

[See it in action!](https://asciinema.org/a/xdYelspxaxpiJ9AhiekNLZtRI)

And checkout [the demo script](./demo.py):

To run the demos, you can execute them with `uv run`:

```bash
uv run python demo/demo.py
uv run python demo/simple_demo.py
```

Or use the convenient just commands:
```bash
just demo
just simple-demo
```

There are also sample helper functions in `typer_shell/samples.py` that you can use in your own applications. These include:

### Sample Commands
- **File Operations**: `ls`, `cat`, `pwd` - basic file system navigation
- **Rich UI**: `table`, `progress`, `panel` - demonstrate rich formatting capabilities  
- **Interactive**: `ask` - prompt for user input with rich styling
- **System**: `env`, `date` - show environment variables and current time
- **Development**: `shell` - drop into IPython with current context

Add them to your shell with:
```python
from typer_shell.samples import add_sample_commands
add_sample_commands(app)
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

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and [ruff](https://docs.astral.sh/ruff/) for linting/formatting.

```bash
# Setup development environment
uv sync

# Run demos
just demo
just simple-demo

# Code quality
just format  # Format code
just lint    # Check for issues
just fix     # Auto-fix issues

# Build and publish
just build
just publish
```
