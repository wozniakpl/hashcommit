import os
from pathlib import Path

from utils import run_hashcommit_command


def test_not_specifying_a_message(initialized_git_repo: Path) -> None:
    result = run_hashcommit_command(
        ["--hash", "a", "--match-type", "begin"],
        cwd=initialized_git_repo,
        expected_returncode=1,
    )
    assert result.stderr.decode().startswith(
        "Error: --message argument is required if not using --overwrite."
    )


def test_not_providing_hash_argument(initialized_git_repo: Path) -> None:
    result = run_hashcommit_command(
        ["--message", "test"], cwd=initialized_git_repo, expected_returncode=1
    )
    assert result.stderr.decode().startswith("Error: --hash argument is required.")


def test_running_outside_of_git_repository(tmp_path: Path) -> None:
    assert os.listdir(tmp_path) == []

    result = run_hashcommit_command(
        ["--message", "test", "--hash", "a"], cwd=tmp_path, expected_returncode=1
    )
    assert result.stderr.decode().startswith("fatal: not a git repository")
