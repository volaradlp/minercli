import requests
import os
import time
import random
import json
from dataclasses import dataclass

from constants import (
    DATA_REGISTRATION_ADDRESS,
    TEE_POOL_ADDRESS,
    ENCRYPTION_SEED,
    VALIDATOR_IMAGE,
    VOLARA_API_KEY,
)
from miner.encrypt import get_encryption_key
from miner.wallet import get_wallet, get_chain_manager
from cli.auth.twitter import get_active_account

data_registry_abi_path = os.path.join(
    os.path.dirname(__file__), "dlp-implementation-abi.json"
)

tee_pool_abi_path = os.path.join(os.path.dirname(__file__), "tee-pool-abi.json")


@dataclass
class ChainConfig:
    network: str


async def submit(file_url: str) -> None:
    """Uploads a file to the Vana DLP implementation.

    Args:
        file_url: The URL of the file to upload to the DLP.
    """
    file_id = await add_file(file_url)


async def add_file(file_url: str) -> int:
    """Adds a file to the Vana DLP implementation.

    Args:
        file_url: The URL of the file to add to the DLP.
    """
    wallet = get_wallet()
    chain_manager = get_chain_manager()
    with open(data_registry_abi_path) as f:
        dlp_contract = chain_manager.web3.eth.contract(
            address=DATA_REGISTRATION_ADDRESS, abi=json.load(f)
        )
    add_file_fn = dlp_contract.functions.addFile(file_url)
    file_id_tx = chain_manager.send_transaction(add_file_fn, wallet.hotkey)
    file_id = int(file_id_tx[1].logs[0]["topics"][1].hex(), 16)
    return file_id


async def submit_tee_request(file_id: int) -> int:
    """Submits a request to the Vana DLP implementation.

    Args:
        file_id: The ID of the file to submit to the DLP.

    Returns:
        The TEE fee amount.
    """
    wallet = get_wallet()
    chain_manager = get_chain_manager()
    with open(tee_pool_abi_path) as f:
        tee_pool_contract = chain_manager.web3.eth.contract(
            address=TEE_POOL_ADDRESS, abi=json.load(f)
        )
    tee_fee_fn = tee_pool_contract.functions.teeFee()
    tee_fee: int = chain_manager.read_contract_fn(tee_fee_fn)

    submit_request_fn = tee_pool_contract.functions.requestContributionProof(file_id)
    submit_request_tx = chain_manager.send_transaction(
        submit_request_fn, wallet.hotkey, value=tee_fee
    )
    block = submit_request_tx[1].blockNumber

    job_id = None
    while True:
        events = tee_pool_contract.events.JobSubmitted.get_logs(fromBlock=block)
        for event in events:
            if event["args"]["fileId"] == file_id:
                job_id = event["args"]["jobId"]
                break
        if job_id is not None:
            break
        time.sleep(1)

    job_tee_fn = tee_pool_contract.functions.jobTee(job_id)
    job_tee = chain_manager.read_contract_fn(job_tee_fn)
    await send_tee_post(job_id, file_id, job_tee[1])
    return tee_amount


async def send_tee_post(job_id: int, file_id: int, tee_url: str) -> None:
    """Sends a TEE post to the Vana DLP implementation.

    Args:
        job_id: The ID of the job to send the TEE post for.
        tee_amount: The amount of TEE to send.
    """
    account = get_active_account()
    if account is None:
        raise ValueError("No active account found")
    cookies = json.dumps(dict(account.session.cookies))
    tee_post_response = requests.post(
        f"{tee_url}/RunProof",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "job_id": job_id,
            "file_id": file_id,
            "encryption_key": get_encryption_key().hex(),
            "encryption_seed": ENCRYPTION_SEED,
            "proof_url": VALIDATOR_IMAGE,
            "env_vars": {
                "FILE_ID": str(file_id),
                "MINER_ADDRESS": get_wallet().hotkey.address,
                "COOKIES": cookies,
            },
            "secrets": {
                "VOLARA_API_KEY": VOLARA_API_KEY,
            },
            "nonce": random.randint(0, 2**16),
        },
    )
    tee_post_response.raise_for_status()
    tee_post_response_json = tee_post_response.json()
    return tee_post_response_json


if __name__ == "__main__":
    import asyncio

    asyncio.run(submit_tee_request(2))
