import pgpy

from pgpy.constants import CompressionAlgorithm, HashAlgorithm
from ecies import encrypt
from eth_account.messages import encode_defunct

from constants import ENCRYPTION_SEED, VOLARA_DLP_OWNER_PUBLIC_KEY_HEX
from miner.wallet import get_wallet


def encrypt_with_public_key(message: str) -> bytes:
    """Encrypts a message with the Vana DLP owner's public key."""
    public_key = VOLARA_DLP_OWNER_PUBLIC_KEY_HEX
    encrypted_message = encrypt(public_key, message.encode())
    return encrypted_message


def get_encryption_key() -> str:
    """Gets the encryption key for the Vana DLP implementation."""
    wallet = get_wallet()
    return wallet.hotkey.sign_message(
        encode_defunct(text=ENCRYPTION_SEED)
    ).signature.hex()


def encrypt_buffer(buffer: bytes) -> bytes:
    """Uploads a file to the Vana DLP implementation.

    Args:
        buffer: The bytes to be encrypted.
    """
    encryption_key = get_encryption_key()
    message = pgpy.PGPMessage.new(buffer, compression=CompressionAlgorithm.ZLIB)
    encrypted_message = message.encrypt(
        passphrase=encryption_key, hash=HashAlgorithm.SHA512
    )
    encrypted_bytes = str(encrypted_message)
    return encrypted_bytes.encode()


if __name__ == "__main__":
    # buffer = b"test"
    # encrypted_buffer = encrypt_buffer(buffer)
    # print(encrypted_buffer)
    print(encrypt_with_public_key("test"))
