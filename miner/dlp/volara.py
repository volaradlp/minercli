import requests
import os
import asyncio
import random
import json
import logging
import aiohttp
from dataclasses import dataclass

from constants import (
    BALANCE_ERROR_STRING,
    DATA_REGISTRATION_ADDRESS,
    DLP_ADDRESS,
    TEE_POOL_ADDRESS,
    ENCRYPTION_SEED,
    VALIDATOR_IMAGE,
    VOLARA_API_KEY,
    VOLARA_DLP_OWNER_ADDRESS,
)
from miner.encrypt import encrypt_with_public_key, get_encryption_key
from miner.wallet import get_wallet, get_chain_manager
from cli.auth.twitter import get_active_account

data_registry_abi_path = os.path.join(
    os.path.dirname(__file__), "data-registry-abi.json"
)
tee_pool_abi_path = os.path.join(os.path.dirname(__file__), "tee-pool-abi.json")
dlp_abi_path = os.path.join(os.path.dirname(__file__), "dlp-abi.json")


@dataclass
class ChainConfig:
    network: str


async def submit(file_url: str) -> None:
    """Uploads a file to the Vana DLP implementation.

    Args:
        file_url: The URL of the file to upload to the DLP.
    """
    logging.info("Adding file...")
    file_id = await _add_file(file_url)
    logging.info("Adding file permission...")
    await _add_file_permission(file_id)
    logging.info("Submitting TEE request...")
    await _submit_tee_request(file_id)
    logging.info("Requesting reward...")
    await _request_reward(file_id)


async def _add_file(file_url: str) -> int:
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
    if file_id_tx is None:
        raise Exception(BALANCE_ERROR_STRING)
    file_id = int(file_id_tx[1].logs[0]["topics"][1].hex(), 16)
    return file_id


async def _add_file_permission(file_id: int) -> None:
    """Adds a file permission to the Vana DLP implementation.

    Args:
        file_id: The ID of the file to add the permission to.
    """
    wallet = get_wallet()
    chain_manager = get_chain_manager()
    with open(data_registry_abi_path) as f:
        dlp_contract = chain_manager.web3.eth.contract(
            address=DATA_REGISTRATION_ADDRESS, abi=json.load(f)
        )
    encryption_key = get_encryption_key()
    encrypted_symmetric_key = encrypt_with_public_key(encryption_key)
    add_file_permission_fn = dlp_contract.functions.addFilePermission(
        file_id, VOLARA_DLP_OWNER_ADDRESS, f"0x{encrypted_symmetric_key.hex()}"
    )
    tx = chain_manager.send_transaction(add_file_permission_fn, wallet.hotkey)
    if tx is None:
        raise Exception(BALANCE_ERROR_STRING)


async def _submit_tee_request(file_id: int) -> None:
    """Submits a request to the Vana DLP implementation.

    Args:
        file_id: The ID of the file to submit to the DLP.
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
        submit_request_fn, wallet.hotkey, value=tee_fee / 10**18
    )
    if submit_request_tx is None:
        raise Exception(BALANCE_ERROR_STRING)

    # Fetch job ID of submitted request
    file_job_ids = tee_pool_contract.functions.fileJobIds(file_id)
    job_ids = chain_manager.read_contract_fn(file_job_ids)
    job_id = job_ids[0]

    # Fetch the job information
    job_fn = tee_pool_contract.functions.jobs(job_id)
    job = chain_manager.read_contract_fn(job_fn)

    # Fetch the assigned TEE information
    tee_address = job[5]
    tees_fn = tee_pool_contract.functions.tees(tee_address)
    tees = chain_manager.read_contract_fn(tees_fn)
    tee_url = tees[1]

    try:
        await send_tee_post(job_id, file_id, tee_url)
    except Exception as e:
        logging.exception("Error sending TEE post!")
        raise e


async def send_tee_post(job_id: int, file_id: int, tee_url: str) -> None:
    """Sends a TEE post to the Vana DLP implementation.

    Args:
        job_id: The ID of the job to send the TEE post for.
        file_id: The ID of the file to send the TEE post for.
        tee_url: The URL of the TEE to send the post to.
    """
    logging.info("Send TEE post...")
    cookies = _get_cookie_str()
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{tee_url}/RunProof",
            headers={
                "Content-Type": "application/json",
            },
            json={
                "job_id": job_id,
                "file_id": file_id,
                "encryption_key": get_encryption_key(),
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
            timeout=None,
            ssl=False,
        ) as response:
            response.raise_for_status()
            tee_post_response_json = await response.json()
            if tee_post_response_json["exit_code"] != 0:
                raise Exception(
                    f"TEE post failed with exit code {tee_post_response_json['exit_code']}"
                )


async def _request_reward(file_id: int) -> None:
    """Requests a reward for a file.

    Args:
        file_id: The ID of the file to request a reward for.
    """
    wallet = get_wallet()
    chain_manager = get_chain_manager()
    with open(dlp_abi_path) as f:
        dlp_contract = chain_manager.web3.eth.contract(
            address=DLP_ADDRESS, abi=json.load(f)
        )
    request_reward_fn = dlp_contract.functions.requestReward(file_id, 1)
    tx = None
    retry_count = 0
    while tx is None:
        tx = chain_manager.send_transaction(request_reward_fn, wallet.hotkey)
        logging.info("Waiting for file proof to be posted...")
        await asyncio.sleep(10)
        retry_count += 1
        if retry_count > 6:
            logging.error("Failed to request reward... proceeding to next file")
            return


def _get_cookie_str() -> str:
    account = get_active_account()
    if account is None:
        raise ValueError("No active account found")
    cookie_dict = dict(account.session.cookies)
    if "personalization_id" in cookie_dict:
        del cookie_dict["personalization_id"]
    if "password" in cookie_dict:
        del cookie_dict["password"]
    if "twid" in cookie_dict:
        cookie_dict["twid"] = cookie_dict["twid"].replace('"', "")
    return json.dumps(cookie_dict)
