import hashlib
import hmac
from app.core.config import settings

def hash_token(token: str) -> str:
    """Hashes a device token using SHA-256."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def verify_device_token(provided_token: str, expected_token_or_hash: str) -> bool:
    """Safely verifies a device token with constant time comparison."""
    if not provided_token or not expected_token_or_hash:
        return False
    # If comparison with raw configured secret
    if hmac.compare_digest(provided_token, expected_token_or_hash):
        return True
    # If comparison with stored hash
    provided_hash = hash_token(provided_token)
    return hmac.compare_digest(provided_hash, expected_token_or_hash)
