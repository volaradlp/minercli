import logging
import click


def set_debug_level(ctx, param, value):
    if value:
        click.echo("Debug logging enabled.")
        logging.basicConfig(level=logging.DEBUG)
    return value


class DebugCommandGroup(click.Group):
    def add_command(self, cmd, name=None):
        cmd.params.insert(
            0,
            click.Option(
                ("--debug", "-d"),
                is_flag=True,
                callback=set_debug_level,
                expose_value=False,
                help="Enable debug logging",
            ),
        )
        super().add_command(cmd, name)
