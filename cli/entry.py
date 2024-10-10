import click

from constants import VERSION

from cli.debug import DebugCommandGroup

import cli.miner as mining
import cli.twitter_entry as twitter_entry
import cli.drive_entry as drive_entry

import cli.auth.twitter as twitter_auth
import cli.auth.drive as drive_auth
import cli.auth.vana as vana_auth

import cli.account.rewards as volara_rewards

import cli.update as volara_update


@click.group(cls=DebugCommandGroup)
@click.version_option(version=VERSION)
@click.pass_context
def volara(ctx):
    """Volora CLI tool"""
    ctx.ensure_object(dict)


@volara.group()
def auth():
    """Commands related to authentication"""
    pass


twitter_entry.register(auth)
drive_entry.register(auth)


@volara.group(cls=DebugCommandGroup)
def mine():
    """Commands related to mining"""
    pass


@mine.command()
@click.option(
    "--background", "-b", is_flag=True, help="Run the miner in a background process"
)
def start(background: bool):
    """Start the mining process"""
    click.echo("Checking Vana credentials...")
    if vana_auth.get_vana_hotkey() is None:
        click.echo(
            "Vana account is not present. Please install the Vana CLI and create a wallet: https://docs.vana.org/vana/for-builders/network-setup/creating-a-wallet#creating-a-local-wallet-with-cli"
        )
        return
    click.echo("Checking drive credentials...")
    if drive_auth.get_active_account() is None:
        click.echo("No active drive account found. Requesting credentials...")
        drive_auth.set_active_account()
    click.echo("Checking twitter account credentials...")
    if twitter_auth.get_active_account() is None:
        click.echo("No active twitter account found. Requesting credentials...")
        if not twitter_auth.set_active_account():
            click.echo("Exiting...")
            return
    click.echo("Starting mining daemon...")
    if background:
        mining.start_daemon()
    else:
        mining.start_inline()


@mine.command()
def stop():
    """Stop the mining process"""
    click.echo("Stopping mining daemon...")
    mining.stop_daemon()


@mine.command()
def logs():
    """Get the logs from the mining process"""
    click.echo("Getting mining logs...")
    mining.echo_logs()


@volara.command()
def update():
    """Update the Volara CLI"""
    volara_update.update_cli()


@volara.group()
def account():
    """Volara account managment."""
    pass


@account.command()
def rewards():
    """Print Volara rewards."""
    volara_rewards.print_rewards()


if __name__ == "__main__":
    volara(obj={})
