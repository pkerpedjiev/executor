import click
from executor.executor import execute


@click.command()
@click.argument("conf_file", default=None)
def cli(conf_file):
    """Example script."""
    execute(conf_file)
