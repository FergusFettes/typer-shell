from click import get_current_context


def running_in_cli():
    get_current_context(silent=True) is not None
