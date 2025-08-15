import os
import tempfile
from typing_extensions import Annotated
from typing import Optional, Callable
from pathlib import Path

import yaml
from typer import Context, Typer, Argument

from rich import print

def add_sample_commands(
        app: Typer,
        params: Optional[dict] = None,
        params_path: Optional[Path] = None,
):
    if params and not params_path:
        params_path = Path(tempfile.NamedTemporaryFile().name)
    if params_path:
        params_path = Path(params_path)
    if params_path and params_path.exists():
        with params_path.open('r') as f:
            params = yaml.load(f, Loader=yaml.FullLoader)

    @app.command(hidden=True)
    def shell(ctx: Context):
        """Drop into an ipython shell"""
        import IPython
        IPython.embed(globals_=globals())

    if not params:
        return

    @app.command()
    def save(ctx: Context):
        """(s) Save the local params to a file"""
        params = ctx.obj.params_groups[ctx.parent.command.name]['params']
        path = ctx.obj.params_groups[ctx.parent.command.name]['path']
        _save(path, params)
        print(f"Saved params to {path}")

    @app.command(name="s", hidden=True)
    def save_alias(ctx: Context):
        save(ctx)

    def _save(path, params):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as f:
            yaml.dump(params, f)

    @app.command()
    def load(ctx: Context):
        """(l) Load the local params from a file"""
        path = ctx.obj.params_groups[ctx.parent.command.name]['path']
        with path.open('r') as f:
            params = yaml.load(f, Loader=yaml.FullLoader)
        ctx.obj.params_groups[ctx.parent.command.name]['params'] = params
        print(f"Loaded params from {path}")

    @app.command(name="l", hidden=True)
    def load_alias(ctx: Context):
        load(ctx)

    @app.command()
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

    @app.command(name="u", hidden=True)
    def update_alias(ctx: Context, name: Annotated[Optional[str], Argument()] = None, value: Annotated[Optional[str], Argument()] = None, kv: Annotated[Optional[str], Argument()] = None):
        update(ctx, name, value, kv)

    def _update(key, value, dict):
        try:
            value = eval(value)
        except (SyntaxError, NameError):
            pass

        # If the value is a string, fix \ns (they should be proper newlines)
        if isinstance(value, str):
            value = value.replace("\\n", "\n").replace("\\t", "\t")

        dict.update({key: value})

    @app.command(name="print")
    def _print(ctx: Context, value: Annotated[Optional[str], Argument()] = None):
        """(p) Print the local params (or a specific value)"""
        params = get_params(ctx)
        if value:
            print(params[value])
        else:
            print(params)

    @app.command(name="p", hidden=True)
    def _print_alias(ctx: Context, value: Annotated[Optional[str], Argument()] = None):
        _print(ctx, value)

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
