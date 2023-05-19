from typing_extensions import Annotated
from typing import Optional, Callable
from pathlib import Path

import click
from click_shell import make_click_shell
from typer import Context, Typer, Argument
from rich.panel import Panel

from rich import print


def make_typer_shell(
        prompt: str = ">> ",
        intro: str = "\n Welcome to typer-shell! Type help to see commands.\n",
        obj: Optional[object] = None,
        default: str = "help",
        params: bool = False,
        params_path: Optional[Path] = None
) -> None:
    """Create a typer shell
        'default' is a default command to run if no command is found
        'obj' is an object to pass to the context
        'params' is a boolean to add a local params command
    """
    app = Typer()
    default = default.replace("_", "-")

    @app.command(hidden=True)
    def help(ctx: Context, command: Annotated[Optional[str], Argument()] = None):
        if command == "help":
            print(Panel(
                "You have found the secret double help!\n"
                ":rainbow: Congratulations! :sparkles:\n"
                "There are a few commands that are hidden from the help menu.\n"
                "One interesting one is 'shell' which will drop you into an ipython shell. With the context.",
                title="Double Help",
                style="bold magenta"
            ))
        print("\n Type 'command --help' or 'help <command>' for help on a specific command.")
        if not command:
            ctx.parent.get_help()
            return
        _command = ctx.parent.command.get_command(ctx, command)
        if _command:
            _command.get_help(ctx)
        else:
            print(f"\n Command not found: {command}")

    def _default(line: str):
        """Default command.
        Unless you override this, it will call the default command
        specified in the constructor with the line as arguments.
        """
        ctx = click.get_current_context()
        default_cmd = (
            ctx.command.get_command(ctx, default)
            or ctx.command.get_command(ctx, 'help')
        )
        try:
            if default_cmd.name == 'help':
                ctx.invoke(default_cmd, ctx=ctx, command=line)
            else:
                ctx.invoke(default_cmd, ctx=ctx, line=line)
            # TODO: Check the signature of the default command and try to pass
            # the arguments as appropriate.
        except Exception as e:
            print(e)
            print(f"Problem running default command: {default}")

    @app.callback(invoke_without_command=True)
    def launch(ctx: Context):
        if obj:
            ctx.obj = obj
        if ctx.invoked_subcommand is None:
            shell = make_click_shell(ctx, prompt=prompt, intro=intro)
            shell.default = _default
            shell.cmdloop()

    @app.command(hidden=True)
    def shell(ctx: Context):
        """Drop into an ipython shell"""
        import IPython
        IPython.embed()

    return app


def params():
   """Create a params object and create functions in the local shell for handling the shell params."""
   pass
