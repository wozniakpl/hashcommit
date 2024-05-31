from pathlib import Path

from utils import get_git_log, run_git_command, run_hashcommit


def test_running_inside_an_empty_git_repository(empty_git_repo: Path) -> None:
    run_git_command(["config", "user.name", "Test User"], cwd=empty_git_repo)
    run_git_command(["config", "user.email", "test@user.com"], cwd=empty_git_repo)
    result = run_hashcommit(
        ["--message", "test", "--hash", "a", "--match-type", "begin"],
        cwd=empty_git_repo,
    )
    assert result.returncode == 0

    git_log = get_git_log(empty_git_repo)
    assert len(git_log) == 1

    assert git_log[0].hash.startswith("a")
    assert git_log[0].message == "test\n"
