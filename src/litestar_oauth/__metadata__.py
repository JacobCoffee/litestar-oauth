"""Project metadata for litestar-oauth.

This module provides version and project information using importlib.metadata
to ensure consistency with package metadata.
"""

from __future__ import annotations

import importlib.metadata

__all__ = ("__project__", "__version__")

__version__ = importlib.metadata.version("litestar-oauth")
__project__ = importlib.metadata.metadata("litestar-oauth")["Name"]
