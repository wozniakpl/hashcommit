import re
from pathlib import Path

from utils import get_git_log, run_hashcommit_command


def test_regex_match(initialized_git_repo: Path) -> None:
    regex_pattern = r"(.)\1"
    run_hashcommit_command(
        ["--hash", regex_pattern, "--message", "test", "--match-type", "regex"],
        cwd=initialized_git_repo,
    )
    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2
    commit_hash = git_log[0].hash
    assert re.search(
        regex_pattern, commit_hash
    ), f"Commit hash {commit_hash} does not match regex {regex_pattern}"


def test_invalid_regex(initialized_git_repo: Path) -> None:
    invalid_regex = r"[invalid"
    result = run_hashcommit_command(
        ["--hash", invalid_regex, "--message", "test", "--match-type", "regex"],
        cwd=initialized_git_repo,
        expected_returncode=2,
    )
    assert "Error: Invalid regular expression pattern" in result.stderr.decode()


def test_complex_regex(initialized_git_repo: Path) -> None:
    # The hash contains two non-overlapping palindromic
    # sequences of length 4, anywhere in the hash.
    # e.g. FAAF...BDDB...
    regex_pattern = r"([0-9a-f])([0-9a-f])\2\1.*([0-9a-f])([0-9a-f])\4\3"
    run_hashcommit_command(
        ["--hash", regex_pattern, "--message", "test", "--match-type", "regex"],
        cwd=initialized_git_repo,
    )
    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2
    commit_hash = git_log[0].hash
    assert re.search(
        regex_pattern, commit_hash
    ), f"Commit hash {commit_hash} does not match regex {regex_pattern}"
