from utils import run_hashcommit_command

from hashcommit.version import VERSION


def test_no_arguments() -> None:
    result = run_hashcommit_command([])
    assert result.stderr.decode().startswith("usage: hashcommit")


def test_help() -> None:
    result = run_hashcommit_command(["--help"])
    assert result.stdout.decode().startswith("usage: hashcommit")


def test_version() -> None:
    result = run_hashcommit_command(["--version"])
    stdout = result.stdout.decode().strip()
    assert stdout.startswith("hashcommit ")
    assert stdout.endswith(VERSION)
