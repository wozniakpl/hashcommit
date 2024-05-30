from utils import run_hashcommit


def test_no_arguments() -> None:
    result = run_hashcommit([])
    assert result.returncode == 0
    assert result.stderr.decode().startswith("usage: hashcommit")


def test_help() -> None:
    result = run_hashcommit(["--help"])
    assert result.returncode == 0
    assert result.stdout.decode().startswith("usage: hashcommit")


def test_version() -> None:
    result = run_hashcommit(["--version"])
    assert result.returncode == 0
