import os
from typing import Annotated, Callable, Optional

import click
from click_shell import make_click_shell
from rich import print
from typer import Argument, Context, Typer


def make_typer_shell(
    prompt: str = ">> ",
    on_finished: Callable = lambda ctx: None,
    intro: str = "\n Welcome to typer-shell! Type help to see commands.\n",
    obj: Optional[object] = None,
    launch: Callable = lambda ctx: None,
    user_callback: Optional[Callable] = None,
) -> Typer:
    """Create a typer shell
    'default' is a default command to run if no command is found
    'obj' is an object to pass to the context
    """
    app = Typer()

    app.command(hidden=True)(help)

    @app.callback(invoke_without_command=True)
    def main(ctx: Context):
        if user_callback:
            user_callback(ctx)

        if obj and not getattr(ctx, "obj", None):
            ctx.obj = obj
        elif obj and getattr(ctx, "obj", None):
            if os.getenv("DEBUG", None):
                print("Warning: There is already an object in the context. The new object will not be added.")

        if ctx.invoked_subcommand is None:
            shell = make_click_shell(ctx, prompt=prompt, intro=intro)
            shell.on_finished = on_finished
            shell.default = _default
            launch(ctx)
            shell.cmdloop()

    return app


def help(ctx: Context, command: Annotated[Optional[str], Argument()] = None):
    if command == "help":
        print("\n Type 'command --help' or 'help <command>' for help on a specific command.")
    if not command:
        ctx.parent.get_help()
        return
    # get_command() is only defined on Group
    if isinstance(ctx.parent.command, click.Group):
        _command = ctx.parent.command.get_command(ctx, command)
    else:
        _command = None
    if _command:
        _command.get_help(ctx)
    else:
        print(f"\n Command not found: {command}")


def _default(line: str):
    """Fixes the click default command to work with typer.
    If there is a function called 'default' in the local context, it will
    be called with the line as an argument. Otherwise, the default command
    is help.
    """
    ctx = click.get_current_context()
    # get_command() is only defined on Group
    if isinstance(ctx.command, click.Group):
        default_cmd = ctx.command.get_command(ctx, "default") or ctx.command.get_command(ctx, "help")
    else:
        default_cmd = ctx.command
    if default_cmd.name == "help":
        ctx.invoke(default_cmd, ctx=ctx, command=line)
    else:
        ctx.invoke(default_cmd, ctx=ctx, line=line)
