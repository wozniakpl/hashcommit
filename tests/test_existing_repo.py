from pathlib import Path

import pytest
from utils import configure_git, get_git_log, run_hashcommit_command


def test_specifying_a_message(initialized_git_repo: Path) -> None:
    run_hashcommit_command(
        ["--hash", "0", "--message", "test"],
        cwd=initialized_git_repo,
    )

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2

    assert git_log[0].message.startswith("test")
    assert git_log[0].hash.startswith("0")


def test_overriding_a_commit(initialized_git_repo: Path) -> None:
    run_hashcommit_command(
        ["--hash", "0", "--message", "test"],
        cwd=initialized_git_repo,
    )

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2
    assert git_log[0].hash.startswith("0")

    run_hashcommit_command(
        ["--hash", "1", "--overwrite"],
        cwd=initialized_git_repo,
    )

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2
    assert git_log[0].hash.startswith("1")


@pytest.mark.parametrize("preserve_author", [True, False])
def test_preserving_original_commit_author(
    initialized_git_repo: Path, preserve_author: bool
) -> None:
    configure_git(initialized_git_repo, "User1", "user1@user.com")

    run_hashcommit_command(
        ["--hash", "0", "--message", "test"],
        cwd=initialized_git_repo,
    )

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2
    assert git_log[0].hash.startswith("0")
    assert git_log[0].author == "User1"

    configure_git(initialized_git_repo, "User2", "user2@user.com")

    args = ["--hash", "1", "--overwrite"]
    if not preserve_author:
        args.append("--no-preserve-author")

    run_hashcommit_command(
        args,
        cwd=initialized_git_repo,
    )

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2
    assert git_log[0].hash.startswith("1")

    if preserve_author:
        assert git_log[0].author == "User1"
    else:
        assert git_log[0].author == "User2"


@pytest.mark.parametrize("preserve_author", [True, False])
def test_overwriting_a_commit_from_the_past(
    initialized_git_repo: Path, preserve_author: bool
) -> None:
    configure_git(initialized_git_repo, "User0", "user0@user.com")
    run_hashcommit_command(
        ["--hash", "0", "--message", "test0"],
        cwd=initialized_git_repo,
    )

    configure_git(initialized_git_repo, "User1", "user1@user.com")
    run_hashcommit_command(
        ["--hash", "1", "--message", "test1"],
        cwd=initialized_git_repo,
    )

    configure_git(initialized_git_repo, "User2", "user2@user.com")
    run_hashcommit_command(
        ["--hash", "2", "--message", "test2"],
        cwd=initialized_git_repo,
    )

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 4

    assert git_log[0].author == "User2"
    assert git_log[0].message.startswith("test2")
    assert git_log[0].hash.startswith("2")

    assert git_log[1].author == "User1"
    assert git_log[1].message.startswith("test1")
    assert git_log[1].hash.startswith("1")

    assert git_log[2].author == "User0"
    assert git_log[2].message.startswith("test0")
    assert git_log[2].hash.startswith("0")

    configure_git(initialized_git_repo, "UserX", "userx@user.com")

    args = ["--hash", "f", "--overwrite", "--commit", git_log[1].hash]
    if not preserve_author:
        args.append("--no-preserve-author")

    run_hashcommit_command(
        args,
        cwd=initialized_git_repo,
    )

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 4

    assert git_log[0].message.startswith("test2")
    assert git_log[0].author == "User2"

    assert git_log[1].message.startswith("test1")
    assert git_log[1].hash.startswith("f")
    if preserve_author:
        assert git_log[1].author == "User1"
    else:
        assert git_log[1].author == "UserX"

    assert git_log[2].message.startswith("test0")
    assert git_log[2].hash.startswith("0")
    assert git_log[2].author == "User0"
