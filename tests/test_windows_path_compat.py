# -*- coding: utf-8 -*-
import pytest

from copaw.agents.tools.send_file import send_file_to_user
from copaw.app.channels.utils import (
    file_url_to_local_path as channel_file_url_to_local_path,
)
from copaw.utils.path_utils import (
    file_url_to_local_path,
    local_path_to_file_url,
)


def _norm_path(path: str | None) -> str | None:
    if path is None:
        return None
    return path.replace("\\", "/")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("file:///C:/tmp/a.txt", "C:/tmp/a.txt"),
        ("file://C:/tmp/a.txt", "C:/tmp/a.txt"),
        ("file://C:\\tmp\\a.txt", "C:/tmp/a.txt"),
        ("C:\\tmp\\a.txt", "C:/tmp/a.txt"),
        ("file://server/share/a.txt", "//server/share/a.txt"),
        ("/tmp/a.txt", "/tmp/a.txt"),
        ("https://example.com/a.txt", None),
        ("s3://bucket/file.txt", None),
    ],
)
def test_file_url_to_local_path_variants(
    value: str,
    expected: str | None,
) -> None:
    assert _norm_path(file_url_to_local_path(value)) == expected


def test_channel_helper_matches_core_parser() -> None:
    value = "file://C:/tmp/a.txt"
    assert channel_file_url_to_local_path(value) == file_url_to_local_path(
        value,
    )


def test_local_path_to_file_url_roundtrip(tmp_path) -> None:
    sample = tmp_path / "demo file.bin"
    sample.write_bytes(b"abc")
    file_url = local_path_to_file_url(str(sample))
    assert file_url.startswith("file://")
    assert " " not in file_url
    assert file_url_to_local_path(file_url) == str(sample.resolve())


@pytest.mark.asyncio
async def test_send_file_to_user_uses_valid_file_url(tmp_path) -> None:
    sample = tmp_path / "demo file.bin"
    sample.write_bytes(b"abc")

    response = await send_file_to_user(str(sample))
    first_block = response.content[0]
    source = first_block.get("source", {})
    url = source.get("url", "")

    assert source.get("type") == "url"
    assert url.startswith("file://")
    assert " " not in url
    assert "%20" in url
