import os

from utils import run_hashcommit


def test_not_providing_hash_argument(initialized_git_repo):
    result = run_hashcommit(["--message", "test"], cwd=initialized_git_repo)
    assert result.returncode == 1
    assert result.stderr.decode().startswith("Error: --hash argument is required.")


def test_running_outside_of_git_repository(tmp_path):
    assert os.listdir(tmp_path) == []

    result = run_hashcommit(["--message", "test", "--hash", "a"], cwd=tmp_path)
    assert result.returncode == 1
    assert result.stderr.decode().startswith("fatal: not a git repository")
