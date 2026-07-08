"""
PJECZ Delphinus Flask CLI
"""

from typer import Typer

from cli.commands.db import db
from cli.commands.usuarios import usuarios

cli = Typer()
cli.add_typer(db, name="db")
cli.add_typer(usuarios, name="usuarios")

if __name__ == "__main__":
    cli()
