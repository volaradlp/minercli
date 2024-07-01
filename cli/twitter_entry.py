import click

import cli.auth.twitter as twitter_auth


def register(auth: click.Group):
    @auth.group()
    def twitter():
        """Manage Twitter Authentication"""
        pass

    @twitter.command()
    def login():
        """Login to Twitter"""
        twitter_auth.set_active_account()

    @twitter.command()
    def logout():
        """Logout from Twitter"""
        twitter_auth.remove_active_account()
