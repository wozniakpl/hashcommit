from pathlib import Path

import pytest
from utils import get_git_log, run_hashcommit


@pytest.mark.xfail(reason="Not implemented yet")
def test_running_inside_an_empty_git_repository(empty_git_repo: Path) -> None:
    result = run_hashcommit(
        ["--message", "test", "--hash", "a", "--match-type", "begin"],
        cwd=empty_git_repo,
    )
    assert result.returncode == 0

    git_log = get_git_log(empty_git_repo)
    assert len(git_log) == 1

    assert git_log[0].hash.startswith("a")
