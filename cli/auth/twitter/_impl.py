import os
from twitter.account import Account
import click
import typing as T
import json

from constants import TMP_TWITTER_AUTH


def get_active_account() -> T.Optional[Account]:
    try:
        with open(TMP_TWITTER_AUTH, "r"):
            pass
        return Account(cookies=TMP_TWITTER_AUTH)
    except FileNotFoundError:
        click.echo("No active account found.")
        return None
    except Exception:
        click.echo("Failed to authenticate.")
        return None


def set_active_account() -> bool:
    click.echo("Setting active twitter account...")
    email = click.prompt("Enter your twitter email")
    username = click.prompt("Enter your twitter username")
    password = click.prompt("Enter your twitter password", hide_input=True)
    try:
        _set_active_account(email, username, password)
    except Exception as e:
        click.echo(click.style(str(e), fg="red"))
        click.echo(
            click.style(f"Failed to authenticate X account {username}.", fg="red"),
            err=True,
        )
        return False
    click.echo("Active twitter account successfully set.")
    return True


def remove_active_account() -> None:
    click.echo("Removing active twitter account...")
    try:
        os.remove(TMP_TWITTER_AUTH)
        click.echo("Active twitter account successfully removed.")
    except FileNotFoundError:
        click.echo("No active twitter account found.")


def _set_active_account(email: str, username: str, password: str) -> None:
    account = Account(email=email, username=username, password=password)
    os.makedirs(os.path.dirname(TMP_TWITTER_AUTH), exist_ok=True)
    with open(TMP_TWITTER_AUTH, "w") as file:
        file.write(json.dumps(dict(account.session.cookies)))
