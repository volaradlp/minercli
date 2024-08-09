from dataclasses import dataclass
import typing as T

import vana


@dataclass
class ChainConfig:
    network: str


def get_vana_hotkey() -> T.Optional[str]:
    try:
        config = vana.Config()
        config.chain = ChainConfig(network="satori")
        wallet = vana.Wallet()
        key = wallet.hotkey.address
        return key
    except Exception:
        return None
