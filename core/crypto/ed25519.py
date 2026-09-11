"""
Ed25519 signing/verification for Vireo v3.1.

Signing flow:
    canonical_bytes = canonical_wire_bytes(envelope)
    h = BLAKE2b-256(canonical_bytes)
    sig = Ed25519_Sign(private_key, h)
"""

from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError
from nacl.encoding import HexEncoder

from .blake2b import wire_hash          # ← ВИПРАВЛЕНО


def generate_keypair() -> dict:
    """Generate a fresh Ed25519 keypair."""
    sk = SigningKey.generate()
    vk = sk.verify_key
    return {
        "private_key_hex": sk.encode(HexEncoder).decode("ascii"),
        "public_key_hex": vk.encode(HexEncoder).decode("ascii"),
    }


def sign_vireo_message(private_key_hex: str, canonical_bytes: bytes) -> str:
    """Sign canonical wire bytes with Ed25519."""
    try:
        sk = SigningKey(bytes.fromhex(private_key_hex))
    except ValueError as e:
        raise ValueError(f"Invalid private key hex: {e}")
    h = wire_hash(canonical_bytes)
    return sk.sign(h).signature.hex()


def verify_vireo_message(
    public_key_hex: str,
    canonical_bytes: bytes,
    signature_hex: str,
) -> tuple[bool, str | None]:
    """Verify an Ed25519 signature over canonical wire bytes."""
    if not public_key_hex:
        return False, "Missing public key"
    if not signature_hex:
        return False, "Missing signature"

    try:
        vk = VerifyKey(bytes.fromhex(public_key_hex))
    except ValueError as e:
        return False, f"Invalid public key: {e}"

    try:
        sig_bytes = bytes.fromhex(signature_hex)
    except ValueError as e:
        return False, f"Invalid signature hex: {e}"

    if len(sig_bytes) != 64:
        return False, f"Ed25519 signature must be 64 bytes, got {len(sig_bytes)}"

    h = wire_hash(canonical_bytes)
    try:
        vk.verify(h, sig_bytes)
        return True, None
    except BadSignatureError:
        return False, "Signature does not match"