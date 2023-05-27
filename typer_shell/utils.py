from pathlib import Path

import click
from click import get_current_context


def running_in_cli():
    get_current_context(silent=True) is not None


class IO:
    @staticmethod
    def get_prompt(prompt, prompt_file):
        """Get the prompt from stdin if it's not provided."""
        if prompt_file:
            prompt = Path(prompt_file).read_text().strip()
            return prompt
        if not prompt:
            click.echo("Reading from stdin... (Ctrl-D to end)", err=True)
            prompt = click.get_text_stream("stdin").read().strip()
            click.echo("Generating...", err=True)
            if not prompt:
                click.echo("No prompt provided. Use the -p flag or pipe a prompt to stdin.", err=True, color="red")
                raise click.Abort()
        return prompt

    @staticmethod
    def return_prompt(response, prompt, prompt_file):
        if prompt_file:
            with open(prompt_file, "a") as f:
                f.write(response)
            return
        sink = click.get_text_stream("stdout")
        if prompt:
            sink.write(prompt + "\n")
        sink.write(response)
