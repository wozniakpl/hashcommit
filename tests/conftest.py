import os

import pytest
from utils import run_git_command


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Set environment variable for tests."""
    os.environ["HASHCOMMIT_TEST"] = "1"


@pytest.fixture
def empty_git_repo(tmp_path):
    """Fixture to create an empty git repository."""
    git_repo = tmp_path / "repo"
    git_repo.mkdir()
    run_git_command(["init"], cwd=git_repo)
    assert os.listdir(git_repo) == [".git"]
    yield git_repo


@pytest.fixture
def initialized_git_repo(empty_git_repo):
    """Fixture to create a git repository with an initial commit."""
    run_git_command(
        ["commit", "--allow-empty", "-m", "Initial commit"], cwd=empty_git_repo
    )
    yield empty_git_repo
