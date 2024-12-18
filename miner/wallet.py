import vana
import os

from eth_account import Account
from dataclasses import dataclass

from constants import NETWORK


@dataclass
class ChainConfig:
    network: str
    chain_endpoint: str | None = None


def get_wallet():
    wallet = vana.Wallet()
    if vana_private_key := os.getenv("VANA_PRIVATE_KEY"):
        account = Account.from_key(vana_private_key)
        wallet._hotkey = account
    return wallet


def get_chain_manager():
    config = vana.Config()
    config.chain = ChainConfig(network=NETWORK)
    if NETWORK == "vana":  # TODO: make this work with Vana lib
        config.chain = ChainConfig(network="https://rpc.vana.org")
    chain_manager = vana.ChainManager(config=config)
    return chain_manager
