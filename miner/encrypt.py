import pgpy

from constants import ENCRYPTION_SEED
from miner.wallet import get_wallet
from eth_account.messages import encode_defunct


def encrypt_buffer(buffer: bytes) -> bytes:
    """Uploads a file to the Vana DLP implementation.

    Args:
        buffer: The bytes to be encrypted.
    """
    wallet = get_wallet()
    encryption_key = bytes(
        wallet.hotkey.sign_message(encode_defunct(text=ENCRYPTION_SEED)).messageHash
    )
    message = pgpy.PGPMessage.new(buffer, file=True)
    encrypted_message = message.encrypt(passphrase=encryption_key)
    encrypted_bytes = bytes(encrypted_message)
    return encrypted_bytes


if __name__ == "__main__":
    buffer = b"test"
    encrypted_buffer = encrypt_buffer(buffer)
    print(encrypted_buffer)
