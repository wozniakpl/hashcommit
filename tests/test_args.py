from typing import List

import pytest
from utils import run_hashcommit_command

from hashcommit.version import VERSION


@pytest.mark.parametrize("args", [[], ["--help"]])
def test_help(args: List[str]) -> None:
    result = run_hashcommit_command(args)
    output = result.stdout.decode()
    assert output.startswith("usage: hashcommit")
    options = [
        "--help",
        "--message",
        "--hash",
        "--match-type",
        "--overwrite",
        "--commit",
        "--no-preserve-author",
        "--verbose",
        "--version",
    ]
    for option in options:
        assert option in output, f"Option {option} not found in output"


def test_version() -> None:
    result = run_hashcommit_command(["--version"])
    stdout = result.stdout.decode().strip()
    assert stdout.startswith("hashcommit ")
    assert stdout.endswith(VERSION)
