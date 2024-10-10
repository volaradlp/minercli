from dataclasses import dataclass
import typing as T
import os

import vana
from eth_account import Account


@dataclass
class ChainConfig:
    network: str


def get_vana_hotkey() -> T.Optional[str]:
    try:
        config = vana.Config()
        config.chain = ChainConfig(network="moksha")
        wallet = vana.Wallet()
        if vana_private_key := os.getenv("VANA_PRIVATE_KEY"):
            account = Account.from_key(vana_private_key)
            wallet._hotkey = account
        key = wallet.hotkey.address
        return key
    except Exception:
        return None
