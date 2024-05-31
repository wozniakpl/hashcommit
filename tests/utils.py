import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


def run_hashcommit_command(
    arguments: List[str],
    env: Optional[Dict] = None,
    cwd: Optional[Path] = None,
    expected_returncode: int = 0,
) -> subprocess.CompletedProcess:
    """Helper function to run hashcommit with given arguments."""
    result = subprocess.run(
        ["hashcommit"] + arguments,
        capture_output=True,
        env=env,
        cwd=cwd,
    )
    assert result.returncode == expected_returncode
    return result


def run_git_command(
    arguments: List[str],
    capture_output: bool = True,
    env: Optional[Dict] = None,
    cwd: Optional[Path] = None,
    expected_returncode: int = 0,
) -> subprocess.CompletedProcess:
    """Helper function to run git commands."""
    result = subprocess.run(
        ["git"] + arguments, capture_output=capture_output, env=env, cwd=cwd
    )
    assert result.returncode == expected_returncode
    return result


@dataclass
class CommitData:
    hash: str
    author: str
    date: str
    message: str


def get_git_log(git_repo: Path) -> List[CommitData]:
    format_str = "%H;%an;%ad;%s"
    log_result = run_git_command(["log", f"--pretty=format:{format_str}"], cwd=git_repo)
    log_lines = list(map(str.strip, log_result.stdout.decode().splitlines()))

    output = []
    for line in log_lines:
        hash_value, author, date, _ = line.split(";")
        message = run_git_command(
            ["log", "-1", "--pretty=format:%B", hash_value], cwd=git_repo
        ).stdout.decode()
        output.append(CommitData(hash_value, author, date, message))
    return output


def configure_git(repo: Path, name: str, email: str) -> None:
    run_git_command(["config", "user.name", name], cwd=repo)
    run_git_command(["config", "user.email", email], cwd=repo)
