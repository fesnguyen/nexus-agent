"""
Utilities for hashing source files.

Responsibilities
----------------
- Compute hashes for files.
- Compare file contents.

This module intentionally does NOT perform:

- File discovery
- Parsing
- Loading
- Index management
"""

from __future__ import annotations

import hashlib
from pathlib import Path


class FileHasher:
    """
    Utility for computing file hashes.
    """

    @staticmethod
    def sha256(path: Path) -> str:
        """
        Compute the SHA-256 hash of a file.
        """

        hasher = hashlib.sha256()

        with path.open("rb") as file:
            while chunk := file.read(8192):
                hasher.update(chunk)

        return hasher.hexdigest()