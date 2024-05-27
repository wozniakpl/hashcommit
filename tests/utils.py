import subprocess
from dataclasses import dataclass
from typing import List


def run_hashcommit(arguments: List[str], env=None, cwd=None):
    """Helper function to run hashcommit with given arguments."""
    command = "hashcommit"
    result = subprocess.run(
        [command] + arguments, capture_output=True, env=env, cwd=cwd
    )
    return result


def run_git_command(arguments: List[str], capture_output=True, env=None, cwd=None):
    """Helper function to run git commands."""
    result = subprocess.run(
        ["git"] + arguments, capture_output=capture_output, env=env, cwd=cwd
    )
    return result


def stripped(arr: List[str]) -> List[str]:
    return list(map(str.strip, arr))


@dataclass
class CommitData:
    hash: str
    author: str
    date: str
    message: str


def get_git_log(git_repo):
    # log_result = run_git_command(["log", "--pretty=fuller"], cwd=git_repo)
    # log_lines = stripped(log_result.stdout.decode().splitlines())
    # return log_lines

    # return list of commits, ordered
    # each commit should have fields: hash, author, date, message

    format_str = "%H;%an;%ad;%s"
    log_result = run_git_command(["log", f"--pretty=format:{format_str}"], cwd=git_repo)
    log_lines = stripped(log_result.stdout.decode().splitlines())

    return [CommitData(*line.split(";")) for line in log_lines]
