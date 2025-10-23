"""Helpers for working with Melco IDs."""
from __future__ import annotations

import re
from typing import Set


_EDGE_HASHES = re.compile(r"^#+|#+$")


def normalize_melco_id(melco_id: str | None) -> str:
    """Return a canonical Melco ID stripped of whitespace and edge hashes."""
    if not melco_id:
        return ""
    trimmed = melco_id.strip()
    if not trimmed:
        return ""
    return _EDGE_HASHES.sub("", trimmed)


def generate_melco_variants(melco_id: str | None) -> Set[str]:
    """
    Produce common Melco ID variants used in legacy datasets.

    The variants include:
    - Original input (trimmed)
    - Canonical value
    - Canonical value prefixed with one or two hashes (historical format)
    """
    if melco_id is None:
        return set()

    trimmed = melco_id.strip()
    if not trimmed:
        return set()

    canonical = normalize_melco_id(trimmed)
    variants = {trimmed}
    if canonical:
        variants.add(canonical)
        variants.add(f"#{canonical}")
        variants.add(f"##{canonical}")
    return variants
