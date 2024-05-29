from utils import get_git_log, run_hashcommit


def test_running_inside_an_existing_git_repository(initialized_git_repo):
    result = run_hashcommit(
        ["--hash", "a", "--match-type", "begin"],
        cwd=initialized_git_repo,
    )
    assert result.returncode == 0

    git_log = get_git_log(initialized_git_repo)
    assert len(git_log) == 2

    assert git_log[0].hash.startswith("a")
