from dataclasses import dataclass
import os
import json

from constants import DLP_ADDRESS
from miner.wallet import get_wallet, get_chain_manager

dlp_implementation_abi_path = os.path.join(
    os.path.dirname(__file__), "dlp-implementation-abi.json"
)


@dataclass
class ChainConfig:
    network: str


async def submit(file_url: str) -> None:
    """Uploads a file to the Vana DLP implementation.

    Args:
        file_url: The URL of the file to upload to the DLP.
    """
    wallet = get_wallet()
    chain_manager = get_chain_manager()
    with open(dlp_implementation_abi_path) as f:
        dlp_contract = chain_manager.web3.eth.contract(
            address=DLP_ADDRESS, abi=json.load(f)
        )
    add_file_fn = dlp_contract.functions.addFile(file_url, "nil")
    chain_manager.send_transaction(add_file_fn, wallet.hotkey)
