import click

import cli.auth.drive as drive_auth


def register(auth: click.Group):
    @auth.group()
    def drive():
        """Manage Google Drive Authentication"""
        pass

    @drive.command()
    def login():
        """Login to Google Drive"""
        drive_auth.set_active_account()

    @drive.command()
    def logout():
        """Logout from Google Drive"""
        drive_auth.remove_active_account()
