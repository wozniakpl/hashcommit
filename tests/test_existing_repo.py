from pathlib import Path

import pytest
from utils import get_git_log, run_git_command, run_hashcommit


def test_specifying_a_message(initialized_git_repo: Path) -> None:
    result = run_hashcommit(
        ["--hash", "0", "--message", "test"],
        cwd=initialized_git_repo,
    )
    assert result.returncode == 0

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2

    assert git_log[0].message.startswith("test")
    assert git_log[0].hash.startswith("0")


def test_overriding_a_commit(initialized_git_repo: Path) -> None:
    result = run_hashcommit(
        ["--hash", "0", "--message", "test"],
        cwd=initialized_git_repo,
    )
    assert result.returncode == 0

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2
    assert git_log[0].hash.startswith("0")

    result = run_hashcommit(
        ["--hash", "1", "--overwrite"],
        cwd=initialized_git_repo,
    )
    assert result.returncode == 0

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2
    assert git_log[0].hash.startswith("1")


@pytest.mark.parametrize("preserve_author", [True, False])
def test_preserving_original_commit_author(
    initialized_git_repo: Path, preserve_author: bool
) -> None:
    run_git_command(["config", "user.name", "User1"], cwd=initialized_git_repo)
    run_git_command(
        ["config", "user.email", "user1@user.com"], cwd=initialized_git_repo
    )

    result = run_hashcommit(
        ["--hash", "0", "--message", "test"],
        cwd=initialized_git_repo,
    )
    assert result.returncode == 0

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2
    assert git_log[0].hash.startswith("0")
    assert git_log[0].author == "User1"

    run_git_command(["config", "user.name", "User2"], cwd=initialized_git_repo)
    run_git_command(
        ["config", "user.email", "user2@user.com"], cwd=initialized_git_repo
    )

    args = ["--hash", "1", "--overwrite"]
    if not preserve_author:
        args.append("--no-preserve-author")

    result = run_hashcommit(
        args,
        cwd=initialized_git_repo,
    )
    assert result.returncode == 0

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2
    assert git_log[0].hash.startswith("1")

    if preserve_author:
        assert git_log[0].author == "User1"
    else:
        assert git_log[0].author == "User2"


def test_overwriting_a_commit_from_the_past(initialized_git_repo: Path) -> None:
    result = run_hashcommit(
        ["--hash", "0", "--message", "test0"],
        cwd=initialized_git_repo,
    )
    assert result.returncode == 0

    result = run_hashcommit(
        ["--hash", "1", "--message", "test1"],
        cwd=initialized_git_repo,
    )
    assert result.returncode == 0

    result = run_hashcommit(
        ["--hash", "2", "--message", "test2"],
        cwd=initialized_git_repo,
    )

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 4
    assert git_log[0].message.startswith("test2")
    assert git_log[0].hash.startswith("2")
    assert git_log[1].message.startswith("test1")
    assert git_log[1].hash.startswith("1")
    assert git_log[2].message.startswith("test0")
    assert git_log[2].hash.startswith("0")

    result = run_hashcommit(
        ["--hash", "f", "--overwrite", "--commit", git_log[1].hash],
        cwd=initialized_git_repo,
    )

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 4
    assert git_log[0].message.startswith("test2")
    # hash of test2 will have changed
    assert git_log[1].message.startswith("test1")
    assert git_log[1].hash.startswith("f")
    assert git_log[2].message.startswith("test0")
    assert git_log[2].hash.startswith("0")
