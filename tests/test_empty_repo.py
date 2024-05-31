from pathlib import Path

from utils import configure_git, get_git_log, run_hashcommit_command


def test_running_inside_an_empty_git_repository(empty_git_repo: Path) -> None:
    configure_git(empty_git_repo, "Test User", "test@user.com")
    result = run_hashcommit_command(
        ["--message", "test", "--hash", "a", "--match-type", "begin"],
        cwd=empty_git_repo,
    )
    assert not result.stderr, result.stderr

    git_log = get_git_log(empty_git_repo)
    assert len(git_log) == 1

    assert git_log[0].hash.startswith("a")
    assert git_log[0].message == "test\n"
