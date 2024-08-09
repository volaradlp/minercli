import os
import click


def update_cli():
    try:
        resp = os.system("git pull")
    except Exception:
        click.echo("Failed to update CLI due to exception.")
        return
    if resp == 0:
        click.echo("CLI updated successfully.")
    else:
        click.echo("Failed to update CLI.")


if __name__ == "__main__":
    update_cli()
