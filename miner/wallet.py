import vana
import os

from eth_account import Account
from dataclasses import dataclass


@dataclass
class ChainConfig:
    network: str


def get_wallet():
    wallet = vana.Wallet()
    if vana_private_key := os.getenv("VANA_PRIVATE_KEY"):
        account = Account.from_key(vana_private_key)
        wallet._hotkey = account
    return wallet


def get_chain_manager():
    config = vana.Config()
    config.chain = ChainConfig(network="moksha")
    chain_manager = vana.ChainManager(config=config)
    return chain_manager
