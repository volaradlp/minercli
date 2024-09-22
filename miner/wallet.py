import vana
from dataclasses import dataclass


@dataclass
class ChainConfig:
    network: str


def get_wallet():
    wallet = vana.Wallet()
    return wallet


def get_chain_manager():
    config = vana.Config()
    config.chain = ChainConfig(network="satori")
    chain_manager = vana.ChainManager(config=config)
    return chain_manager
