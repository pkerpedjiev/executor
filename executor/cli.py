import click
from executor.executor import execute


@click.command()
@click.argument('base_dir')
def cli(base_dir):
    """Example script."""
    execute(base_dir)
