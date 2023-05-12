from typing_extensions import Annotated
from typing import Optional, Callable

from click_shell import make_click_shell
from click_shell.core import get_invoke
from typer import Context, Typer, Argument

from rich import print


def check_aliases(app: Typer, ctx: Context, args: str) -> None:
    """Check if the command is an alias and run it if it is"""
    if not args:
        return
    args = args.split()
    command = args[0]
    if len(args) > 1:
        args = args[1:]
    else:
        args = None

    unaliased = app.aliases.get(command, None)
    if not unaliased:
        print("Command not found. Type 'help' to see commands.")
        return

    root = ctx.find_root()
    command = root.command.get_command(ctx, unaliased)
    __import__('ipdb').set_trace()
    command = get_invoke(command)
    if args:
        # For this to work with real commands, you need some way of formatting the rest of the arguments.
        ctx.invoke(command, args=args)
    else:
        ctx.invoke(command)


def make_typer_shell(
        app: Typer,
        prompt: str = ">> ",
        intro: str = "\n Welcome to typer-shell! Type help to see commands.\n",
        default: Callable = check_aliases,
        obj: Optional[object] = None,
) -> None:
    app.aliases = {
        "h": "help",
    }

    @app.command(hidden=True)
    def help(ctx: Context, command: Annotated[Optional[str], Argument()] = None):
        print("\n Type 'command --help' or 'help <command>' for help on a specific command.")
        if not command:
            ctx.parent.get_help()
            return
        ctx.parent.command.get_command(ctx, command).get_help(ctx)

    @app.command(hidden=True)
    def _default(ctx: Context, args: str):
        """Default command"""
        if default:
            default(app, ctx, args)
        else:
            print("Command not found. Type 'help' to see commands.")

    @app.callback(invoke_without_command=True)
    def launch(ctx: Context):
        if obj:
            ctx.obj = obj
        if ctx.invoked_subcommand is None:
            shell = make_click_shell(ctx, prompt=prompt, intro=intro)
            root = ctx.find_root()
            command = root.command.get_command(ctx, "-default")
            shell.default = command
            shell.cmdloop()

    @app.command(hidden=True)
    def shell(ctx: Context):
        """Drop into an ipython shell"""
        import IPython
        IPython.embed()
