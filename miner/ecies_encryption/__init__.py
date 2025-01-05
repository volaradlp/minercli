import os
from typing import Union
from coincurve import PrivateKey, PublicKey
from ecies.utils import hex2pk
from Crypto.Hash import SHA512, HMAC, SHA256
from Crypto.Cipher import AES


def ecies_encrypt(
    receiver_pk: Union[str, bytes], msg: bytes
) -> tuple[bytes, PrivateKey, bytes]:
    """
    Encrypt with receiver's secp256k1 public key

    Parameters
    ----------
    receiver_pk: Union[str, bytes]
        Receiver's public key (hex str or bytes)
    msg: bytes
        Data to encrypt

    Returns
    -------
    bytes
        Encrypted data
    """
    if isinstance(receiver_pk, str):
        pk = hex2pk(receiver_pk)
    elif isinstance(receiver_pk, bytes):
        pk = PublicKey(receiver_pk)
    else:
        raise TypeError("Invalid public key type")

    # Generate ephemeral key pair
    ephemeral_sk = PrivateKey()
    ephemeral_pk = ephemeral_sk.public_key.format(compressed=False)

    # Derive shared secret
    shared_point = pk.multiply(ephemeral_sk.secret)
    px = shared_point.format(compressed=True)[1:]

    # Generate encryption and MAC keys using SHA512
    hash_px = SHA512.new(px).digest()
    encryption_key = hash_px[:32]
    mac_key = hash_px[32:]

    # Generate IV and encrypt
    iv = os.urandom(16)
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    padding_length = 16 - (len(msg) % 16)
    padded_msg = msg + bytes([padding_length] * padding_length)
    encrypted = cipher.encrypt(padded_msg)

    # Generate MAC
    data_to_mac = b"".join([iv, ephemeral_pk, encrypted])
    mac = HMAC.new(mac_key, data_to_mac, SHA256).digest()[:32]

    # Combine all components
    rsp = iv + ephemeral_pk + encrypted + mac
    return rsp, ephemeral_sk, iv
