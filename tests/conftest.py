from pathlib import Path
from typing import Generator

import pytest
from utils import configure_git, run_git_command


@pytest.fixture
def empty_git_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """Fixture to create an empty git repository."""
    git_repo = tmp_path / "repo"
    git_repo.mkdir()
    run_git_command(["init"], cwd=git_repo)
    yield git_repo


@pytest.fixture
def initialized_git_repo(empty_git_repo: Path) -> Generator[Path, None, None]:
    """Fixture to create a git repository with an initial commit."""
    configure_git(empty_git_repo, "Test User", "test@user.com")
    result = run_git_command(
        ["commit", "--allow-empty", "-m", "Initial commit"], cwd=empty_git_repo
    )
    assert not result.stderr, result.stderr
    assert run_git_command(["log"], cwd=empty_git_repo).stdout
    yield empty_git_repo
