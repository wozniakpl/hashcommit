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
    assert run_git_command(["rev-parse", "HEAD"], cwd=git_repo).stdout
    yield git_repo


@pytest.fixture
def initialized_git_repo(empty_git_repo):
    """Fixture to create a git repository with an initial commit."""
    run_git_command(["config", "user.name", "Test User"], cwd=empty_git_repo)
    run_git_command(["config", "user.email", "test@user.com"], cwd=empty_git_repo)
    result = run_git_command(
        ["commit", "--allow-empty", "-m", "Initial commit"], cwd=empty_git_repo
    )
    assert result.returncode == 0
    assert not result.stderr, result.stderr
    assert run_git_command(["log"], cwd=empty_git_repo).stdout
    yield empty_git_repo
