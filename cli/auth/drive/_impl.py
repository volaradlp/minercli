import typing as T
import os
import click
import requests
import json
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from constants import TMP_DRIVE_AUTH, VOLARA_API

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_active_account() -> T.Optional[Credentials]:
    if os.path.exists(TMP_DRIVE_AUTH):
        with open(TMP_DRIVE_AUTH, "r") as token:
            code = json.load(token)
            code["expiry"] = dt.datetime.fromisoformat(code["expiry"][:-1]).replace(
                tzinfo=None
            )
            creds = Credentials(**code)
        if creds.expired:
            click.echo("Current session is expired... requesting new credentials")
            creds = _call_volara_api_server_refresh(creds)
            if creds is not None:
                _persist_credentials(creds)
            return creds
        if creds.valid:
            return creds
    return None


def set_active_account() -> T.Optional[Credentials]:
    if os.path.exists(TMP_DRIVE_AUTH):
        os.remove(TMP_DRIVE_AUTH)
        click.echo("Removed existing active account.")
    click.echo("Setting active account...")
    creds = _call_volara_api_server()
    if not creds:
        click.echo("Failed to get the drive auth code from Volara's auth server.")
        return
    _persist_credentials(creds)
    click.echo("Active account set.")
    return creds


def remove_active_account() -> None:
    click.echo("Removing active account...")
    if os.path.exists(TMP_DRIVE_AUTH):
        os.remove(TMP_DRIVE_AUTH)
        click.echo("Active account removed.")
    else:
        click.echo("No active account found.")


def _persist_credentials(creds: Credentials) -> None:
    os.makedirs(os.path.dirname(TMP_DRIVE_AUTH), exist_ok=True)
    with open(TMP_DRIVE_AUTH, "w") as token:
        token.write(creds.to_json())


def _call_volara_api_server() -> T.Optional[Credentials]:
    url_response = requests.get(f"{VOLARA_API}/auth/get-url")
    if url_response.status_code != 200:
        return
    url = url_response.json()["url"]
    click.echo(f"Copy and paste this URL into your browser: {url}")
    code = click.prompt("Paste your code")
    code_response = requests.get(f"{VOLARA_API}/auth/callback?code={code}")
    code_response.raise_for_status()
    if code_response.status_code != 200:
        return
    resp = code_response.json()["tokens"]
    return _form_credentials_from_token(resp)


def _call_volara_api_server_refresh(creds: Credentials) -> T.Optional[Credentials]:
    url_response = requests.get(f"{VOLARA_API}/auth/refresh?refreshToken={creds.token}")
    if url_response.status_code != 200:
        return
    resp = url_response.json()["tokens"]
    return _form_credentials_from_token(resp)


def _form_credentials_from_token(resp: T.Dict[str, T.Any]) -> Credentials:
    code = {
        "token": resp["access_token"],
        "scopes": [resp["scope"]],
        "expiry": dt.datetime.fromtimestamp(
            resp["expiry_date"] / 1000, dt.timezone.utc
        ),
    }
    return Credentials(**code)
