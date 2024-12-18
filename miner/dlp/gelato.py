import aiohttp
import time
import asyncio

from constants import (
    DATA_REGISTRATION_ADDRESS,
    DLP_ADDRESS,
    GELATO_API_KEY,
    GELATO_API_URL,
    TEE_POOL_ADDRESS,
    VOLARA_DLP_OWNER_ADDRESS,
)
from miner.dlp.contracts import get_dlp_contract
from miner.wallet import get_chain_manager, get_wallet
from miner.dlp.eip712 import eip712_encode, eip712_signature


def _form_eip712_message_sponsored_call_erc2771(
    chain_id: int,
    user: str,
    user_nonce: int,
    user_deadline: int,
    target: str,
    data: str,
):
    eip712_data = {
        "domain": {
            "name": "GelatoRelay1BalanceERC2771",
            "version": "1",
            "chainId": chain_id,
            "verifyingContract": "0x61f2976610970afedc1d83229e1e21bdc3d5cbe4",
        },
        "message": {
            "userDeadline": user_deadline,
            "chainId": chain_id,
            "target": target,
            "data": bytes.fromhex(data[2:]),
            "user": user,
            "userNonce": user_nonce,
        },
        "primaryType": "SponsoredCallERC2771",
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "SponsoredCallERC2771": [
                {"name": "chainId", "type": "uint256"},
                {"name": "target", "type": "address"},
                {"name": "data", "type": "bytes"},
                {"name": "user", "type": "address"},
                {"name": "userNonce", "type": "uint256"},
                {"name": "userDeadline", "type": "uint256"},
            ],
        },
    }
    return eip712_encode(eip712_data)


async def _send_relay_2711_http_post(
    request: dict,
):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{GELATO_API_URL}/relays/v2/sponsored-call-erc2771/",
            headers={
                "Content-Type": "application/json",
            },
            json=request,
        ) as response:
            response.raise_for_status()
            return await response.json()


async def _send_relay_http_post(request: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{GELATO_API_URL}/relays/v2/sponsored-call/",
            headers={
                "Content-Type": "application/json",
            },
            json=request,
        ) as response:
            response.raise_for_status()
            return await response.json()


async def _get_nonce_2771(chain_manager, user_address: str) -> int:
    nonce_contract = chain_manager.web3.eth.contract(
        address="0x61F2976610970AFeDc1d83229e1E21bdc3D5cbE4",
        abi=[
            {
                "inputs": [
                    {"internalType": "address", "name": "user", "type": "address"}
                ],
                "name": "userNonce",
                "outputs": [
                    {"internalType": "uint256", "name": "nonce", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function",
            }
        ],
    )
    return nonce_contract.functions.userNonce(user_address).call()


async def _wait_for_task_submission(task_id: str):
    tx_hash = ""
    while not tx_hash:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://relay.gelato.digital/tasks/status/{task_id}",
            ) as response:
                response.raise_for_status()
                status_data = await response.json()
                if "transactionHash" in status_data["task"]:
                    tx_hash = status_data["task"]["transactionHash"]
                if "Pending" not in status_data["task"]["taskState"] and not tx_hash:
                    raise Exception(f"Gelato relay failed {status_data}")
                await asyncio.sleep(1)
    return tx_hash


async def _send_relay_2771_request(
    data: str,
    target: str,
):
    wallet = get_wallet()
    chain_manager = get_chain_manager()

    nonce = await _get_nonce_2771(chain_manager, wallet.hotkey.address)
    deadline = int(time.time()) + 120
    eip_712_message = _form_eip712_message_sponsored_call_erc2771(
        chain_manager.web3.eth.chain_id,
        wallet.hotkey.address,
        nonce,
        deadline,
        target,
        data,
    )
    request = {
        "chainId": chain_manager.web3.eth.chain_id,
        "target": target,
        "data": data,
        "user": wallet.hotkey.address,
        "userNonce": nonce,
        "userDeadline": deadline,
        "userSignature": eip712_signature(
            eip_712_message, wallet.hotkey._private_key.hex()
        ),
        "sponsorApiKey": GELATO_API_KEY,
    }
    post_response = await _send_relay_2711_http_post(request)
    tx_hash = await _wait_for_task_submission(post_response["taskId"])
    receipt = chain_manager.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt["status"] != 1:
        raise Exception(
            f"Transaction failed: Receipt of Gelato request is bad {tx_hash}"
        )
    return receipt


async def _send_relay_request(data: str, target: str):
    chain_manager = get_chain_manager()

    request = {
        "chainId": chain_manager.web3.eth.chain_id,
        "target": target,
        "data": data,
        "sponsorApiKey": GELATO_API_KEY,
    }
    post_response = await _send_relay_http_post(request)
    tx_hash = await _wait_for_task_submission(post_response["taskId"])
    receipt = chain_manager.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt["status"] != 1:
        raise Exception(
            f"Transaction failed: Receipt of Gelato request is bad {tx_hash}"
        )
    return receipt


async def send_add_file_relay_request(
    data_registry_contract,
    file_url: str,
) -> int:
    data = data_registry_contract.encodeABI(fn_name="addFile", args=[file_url])
    receipt = await _send_relay_2771_request(data, DATA_REGISTRATION_ADDRESS)
    return int(receipt["logs"][0]["topics"][1].hex(), 16)


async def send_add_file_permission_relay_request(
    data_registry_contract, file_id: int, encrypted_symmetric_key: str
):
    data = data_registry_contract.encodeABI(
        fn_name="addFilePermission",
        args=[file_id, VOLARA_DLP_OWNER_ADDRESS, encrypted_symmetric_key],
    )
    await _send_relay_2771_request(data, DATA_REGISTRATION_ADDRESS)


async def send_request_contribution_proof_relay_request(
    tee_pool_contract, file_id: int
):
    data = tee_pool_contract.encodeABI(
        fn_name="requestContributionProof", args=[file_id]
    )
    await _send_relay_2771_request(data, TEE_POOL_ADDRESS)


async def send_request_reward_relay_request(dlp_contract, file_id: int):
    data = dlp_contract.encodeABI(fn_name="requestReward", args=[file_id, 1])
    await _send_relay_request(data, DLP_ADDRESS)


if __name__ == "__main__":
    dlp_contract = get_dlp_contract()
    resp = asyncio.run(send_request_reward_relay_request(dlp_contract, 123333))
    print(resp)
