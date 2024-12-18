import requests
import vana
import os
import click
import typing as T

from eth_account.messages import encode_defunct

from constants import TMP_VOLARA_TOKEN, VOLARA_API


def _request_challenge():
    wallet = vana.Wallet()
    resp = requests.post(
        f"{VOLARA_API}/v1/auth/get-message",
        json={"walletAddress": wallet.hotkey.address},
    )
    resp.raise_for_status()
    return resp.json()["challenge"]


def _submit_signature(challenge):
    wallet = vana.Wallet()
    message = encode_defunct(text=challenge["message"])
    signature = wallet.hotkey.sign_message(message).signature.hex()
    resp = requests.post(
        f"{VOLARA_API}/v1/auth/submit-signature",
        json={"signature": signature, "extraData": challenge["extraData"]},
    )
    resp.raise_for_status()
    return resp.json()["accessToken"]


def _get_volara_jwt() -> T.Optional[str]:
    challenge = _request_challenge()
    jwt = _submit_signature(challenge)
    return jwt


def get_volara_jwt() -> T.Optional[str]:
    if os.path.exists(TMP_VOLARA_TOKEN):
        with open(TMP_VOLARA_TOKEN, "r") as f:
            return f.read()
    try:
        jwt = _get_volara_jwt()
    except Exception as e:
        click.echo(f"Error getting Volara JWT: {e}")
        return None
    if jwt:
        if os.path.exists(TMP_VOLARA_TOKEN):
            os.remove(TMP_VOLARA_TOKEN)
        with open(TMP_VOLARA_TOKEN, "w") as f:
            f.write(jwt)
        return jwt
    click.echo("Error getting Volara JWT")
