from pathlib import Path

import pytest
from utils import configure_git, run_git_command, run_hashcommit_command


def get_unreachable_commits(repo: Path) -> list[str]:
    result = run_git_command(["fsck", "--unreachable"], cwd=repo)
    return [
        line.split()[2]
        for line in result.stdout.decode().splitlines()
        if line.startswith("unreachable commit")
    ]


@pytest.mark.xfail(reason="Not implemented yet")
def test_not_leaving_unreachable_commits(empty_git_repo: Path) -> None:
    configure_git(empty_git_repo, "Test User", "test@user.com")
    assert not get_unreachable_commits(empty_git_repo)

    run_hashcommit_command(
        ["--message", "test", "--hash", "a"],
        cwd=empty_git_repo,
    )
    assert not get_unreachable_commits(empty_git_repo)

    run_hashcommit_command(
        ["--message", "test", "--hash", "b", "--overwrite"],
        cwd=empty_git_repo,
    )
    assert not get_unreachable_commits(empty_git_repo)
