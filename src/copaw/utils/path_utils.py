# -*- coding: utf-8 -*-
"""Path helpers for cross-platform local path and file URL conversion."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from urllib.request import url2pathname

_WINDOWS_DRIVE_NETLOC_RE = re.compile(r"^[A-Za-z]:$")
_WINDOWS_DRIVE_PATH_RE = re.compile(r"^/[A-Za-z]:[/\\]")
_WINDOWS_LOCAL_PATH_RE = re.compile(r"^[A-Za-z]:[\\/]")


def _looks_like_windows_local_path(value: str) -> bool:
    return bool(_WINDOWS_LOCAL_PATH_RE.match(value) or value.startswith("\\\\"))


def file_url_to_local_path(url: str) -> Optional[str]:
    """Convert ``file://`` URL or plain local path to local path string.

    Returns ``None`` only when ``url`` is clearly not a local file path
    (for example http/https URL or unsupported scheme).
    """
    if not isinstance(url, str):
        return None
    s = url.strip()
    if not s:
        return None

    parsed = urlparse(s)
    if parsed.scheme == "file":
        if parsed.netloc and not parsed.path:
            netloc = parsed.netloc
            if _looks_like_windows_local_path(netloc):
                return netloc
            path = url2pathname(f"//{netloc}")
            return path if path else None

        if parsed.netloc and parsed.path:
            if _WINDOWS_DRIVE_NETLOC_RE.match(parsed.netloc):
                path = url2pathname(f"{parsed.netloc}{parsed.path}")
                return path if path else None
            path = url2pathname(f"//{parsed.netloc}{parsed.path}")
            return path if path else None

        path = parsed.path
        if _WINDOWS_DRIVE_PATH_RE.match(path):
            path = path[1:]
        path = url2pathname(path)
        return path if path else None

    if parsed.scheme in ("http", "https"):
        return None

    if not parsed.scheme:
        return s

    # Windows path like C:\foo may be parsed as scheme="c", path="\\foo".
    if len(parsed.scheme) == 1 and parsed.path.startswith(("/", "\\")):
        return s

    return None


def local_path_to_file_url(path: str) -> str:
    """Convert a local path string to ``file://`` URL."""
    local_path = Path(path).expanduser()
    try:
        local_path = local_path.resolve()
    except OSError:
        local_path = local_path.absolute()
    return local_path.as_uri()
