import os
import tempfile
from typing_extensions import Annotated
from typing import Optional, Callable
from pathlib import Path

import yaml
import click
from click_shell import make_click_shell
from typer import Context, Typer, Argument

from rich import print


def make_typer_shell(
        prompt: str = ">> ",
        intro: str = "\n Welcome to typer-shell! Type help to see commands.\n",
        obj: Optional[object] = None,
        params: Optional[dict] = None,
        params_path: Optional[Path] = None,
        launch: Callable = lambda ctx: None,
) -> None:
    """Create a typer shell
        'default' is a default command to run if no command is found
        'obj' is an object to pass to the context
        'params' is a boolean to add a local params command
    """
    app = Typer()

    app.command(hidden=True)(help)
    app.command(hidden=True)(shell)

    if params and not params_path:
        params_path = Path(tempfile.NamedTemporaryFile().name)
    if params_path:
        params_path = Path(params_path)
    if params_path and params_path.exists():
        with params_path.open('r') as f:
            params = yaml.load(f, Loader=yaml.FullLoader)

    @app.callback(invoke_without_command=True)
    def main(ctx: Context):
        _obj(ctx, params, params_path, obj)
        if ctx.invoked_subcommand is None:
            shell = make_click_shell(ctx, prompt=prompt, intro=intro)
            shell.default = _default
            launch(ctx)
            shell.cmdloop()

    if params:
        app.command()(save)
        app.command(name="s", hidden=True)(save)
        app.command()(load)
        app.command(name="l", hidden=True)(load)
        app.command()(update)
        app.command(name="u", hidden=True)(update)
        app.command(name="print")(_print)
        app.command(name="p", hidden=True)(_print)

    return app


def _obj(
        ctx: Context,
        params: Optional[dict] = None,
        params_path: Optional[Path] = None,
        obj: Optional[object] = None
):
    # If there is an object and params, make sure the object has a field in the params dict for the shell
    # If there is no object and params, make a fkae object for holding the dicts
    # If this is not the main shell and there is already an object from the main shell, print a warning
    if not obj and not params and not params_path:
        return

    # First ensure obj
    if obj and not getattr(ctx, 'obj'):
        ctx.obj = obj
    elif obj and getattr(ctx, 'obj'):
        if os.getenv("DEBUG", None):
            print("Warning: There is already an object in the context. The new object will not be added.")
    elif not obj and not getattr(ctx, 'obj') and params:
        class _obj:
            pass
        ctx.obj = _obj()

    assert ctx.obj, "There is no object in the context. This should not happen."

    # Then add the params
    if params:
        add_params(ctx, params, params_path, ctx.command.name)


def add_params(ctx, params, params_path, name):
    params_dict = {name: {"params": params, "path": params_path}}
    existing = getattr(ctx.obj, 'params_groups', None)
    if not existing:
        ctx.obj.params_groups = {}
    elif name in existing:
        return
    ctx.obj.params_groups.update(params_dict)
    # And save them to file
    _save(params_path, params)


def help(ctx: Context, command: Annotated[Optional[str], Argument()] = None):
    if command == "help":
        print("\n Type 'command --help' or 'help <command>' for help on a specific command.")
        # print(Panel(
        #     "You have found the secret double help!\n"
        #     ":rainbow: Congratulations! :sparkles:\n"
        #     "There are a few commands that are hidden from the help menu.\n"
        #     "One interesting one is 'shell' which will drop you into an ipython shell. With the context.",
        #     title="Double Help",
        #     style="bold magenta"
        # ))
    if not command:
        ctx.parent.get_help()
        return
    _command = ctx.parent.command.get_command(ctx, command)
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
    default_cmd = (
        ctx.command.get_command(ctx, "default")
        or ctx.command.get_command(ctx, 'help')
    )
    if default_cmd.name == 'help':
        ctx.invoke(default_cmd, ctx=ctx, command=line)
    else:
        ctx.invoke(default_cmd, ctx=ctx, line=line)
    # TODO: Check the signature of the default command and try to pass
    # the arguments as appropriate.


def shell(ctx: Context):
    """Drop into an ipython shell"""
    import IPython
    IPython.embed(globals_=globals())


def save(ctx: Context):
    """(s) Save the local params to a file"""
    params = ctx.obj.params_groups[ctx.parent.command.name]['params']
    path = ctx.obj.params_groups[ctx.parent.command.name]['path']
    _save(path, params)
    print(f"Saved params to {path}")


def _save(path, params):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w') as f:
        yaml.dump(params, f)


def load(ctx: Context):
    """(l) Load the local params from a file"""
    path = ctx.obj.params_groups[ctx.parent.command.name]['path']
    with path.open('r') as f:
        params = yaml.load(f, Loader=yaml.FullLoader)
    ctx.obj.params_groups[ctx.parent.command.name]['params'] = params
    print(f"Loaded params from {path}")


def update(
    ctx: Context,
    name: Annotated[Optional[str], Argument()] = None,
    value: Annotated[Optional[str], Argument()] = None,
    kv: Annotated[Optional[str], Argument()] = None,
):
    "(u) Update a config value, or set of values. (kv in the form of 'name1=value1,name2=value2')"
    params = ctx.obj.params_groups[ctx.parent.command.name]['params']
    if kv:
        updates = kv.split(",")
        for kv in updates:
            name, value = kv.split("=")
            _update(name, value, params)
    if name and value is not None:
        _update(name, value, params)
    if not name and not value and not kv:
        for key, value in params.items():
            value = input(f"{key} [{value}]: ")
            if not value:
                continue
            _update(key, value, params)
    print(params)


def _update(key, value, dict):
    try:
        value = eval(value)
    except (SyntaxError, NameError):
        pass

    # If the value is a string, fix \ns (they should be proper newlines)
    if isinstance(value, str):
        value = value.replace("\\n", "\n").replace("\\t", "\t")

    dict.update({key: value})


def _print(ctx: Context, value: Annotated[Optional[str], Argument()] = None):
    """(p) Print the local params (or a specific value)"""
    params = get_params(ctx)
    if value:
        print(params[value])
    else:
        print(params)


def get_params(ctx, name=None):
    return get_params_full(ctx, name).get("params", {})


def get_params_path(ctx, name=None):
    return Path(get_params_full(ctx, name).get("path", ""))


def get_params_full(ctx, _name=None):
    name = _name or ctx.command.name
    if name not in ctx.obj.params_groups:
        if ctx.parent and _name is None:
            name = ctx.parent.command.name
    if name not in ctx.obj.params_groups:
        if os.getenv("DEBUG", None):
            print("Cant find params!")
    else:
        return ctx.obj.params_groups[name]
    return {}
