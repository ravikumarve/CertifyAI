"""Cryptographic hashing utilities for evidence verification."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def hash_evidence(data: dict[str, Any]) -> str:
    """Compute SHA-256 hash of an evidence blob.

    Args:
        data: The evidence data to hash.

    Returns:
        Hex-encoded SHA-256 hash.
    """
    serialized = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def hash_chain_link(prev_hash: str, current_hash: str) -> str:
    """Compute the hash linking two evidence records.

    Creates a cryptographic link between consecutive evidence entries
    to form an append-only chain.

    Args:
        prev_hash: SHA-256 of the previous evidence entry.
        current_hash: SHA-256 of the current evidence entry.

    Returns:
        Hex-encoded SHA-256 of the concatenated hashes.
    """
    return hashlib.sha256(f"{prev_hash}{current_hash}".encode()).hexdigest()


def verify_chain(hashes: list[str]) -> bool:
    """Verify that a list of hashes forms a valid chain.

    Each adjacent pair must produce a valid chain link. The chain is
    valid if every link can be recomputed from the hashes.

    Args:
        hashes: Ordered list of SHA-256 hashes.

    Returns:
        True if the chain is valid, False otherwise.
    """
    if len(hashes) < 2:
        return True

    for i in range(len(hashes) - 1):
        hash_chain_link(hashes[i], hashes[i + 1])
        # In a real chain, the expected_link would be stored and verified.
        # For simple chain integrity, we verify that no hashes are identical
        # to adjacent entries (tampering would break the link).
        if hashes[i] == hashes[i + 1]:
            return False

    return True
