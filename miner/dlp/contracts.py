import os
import json
from web3.contract.contract import Contract

from constants import DATA_REGISTRATION_ADDRESS, DLP_ADDRESS, TEE_POOL_ADDRESS
from miner.wallet import get_chain_manager


data_registry_abi_path = os.path.join(
    os.path.dirname(__file__), "data-registry-abi.json"
)
tee_pool_abi_path = os.path.join(os.path.dirname(__file__), "tee-pool-abi.json")
dlp_abi_path = os.path.join(os.path.dirname(__file__), "dlp-abi.json")


def get_data_registry_contract() -> Contract:
    chain_manager = get_chain_manager()
    with open(data_registry_abi_path) as f:
        return chain_manager.web3.eth.contract(
            address=DATA_REGISTRATION_ADDRESS, abi=json.load(f)
        )


def get_tee_pool_contract() -> Contract:
    chain_manager = get_chain_manager()
    with open(tee_pool_abi_path) as f:
        return chain_manager.web3.eth.contract(
            address=TEE_POOL_ADDRESS, abi=json.load(f)
        )


def get_dlp_contract() -> Contract:
    chain_manager = get_chain_manager()
    with open(dlp_abi_path) as f:
        return chain_manager.web3.eth.contract(address=DLP_ADDRESS, abi=json.load(f))
