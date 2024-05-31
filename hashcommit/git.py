import os
import subprocess
from typing import Dict, Optional


def is_in_git_repo() -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=False,
            stdout=subprocess.PIPE,
        ).returncode
        == 0
    )


def does_repo_have_any_commits() -> bool:
    try:
        subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def create_git_env(timestamp: str) -> Dict[str, str]:
    return {
        **os.environ,
        "GIT_AUTHOR_DATE": timestamp,
        "GIT_COMMITTER_DATE": timestamp,
    }


def get_tree_hash() -> str:
    result = subprocess.run(
        ["git", "write-tree"],
        stdout=subprocess.PIPE,
        check=True,
    )
    return result.stdout.decode("utf-8").strip()


def get_head_hash() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            check=True,
        )
        return result.stdout.decode("utf-8").strip()
    except subprocess.CalledProcessError:
        return None


def get_parent_head_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD^"],
            stdout=subprocess.PIPE,
            check=True,
        )
        value = result.stdout.decode("utf-8").strip()
        if not value:
            raise ValueError("Empty HEAD^ hash")
        return value
    except subprocess.CalledProcessError:
        raise ValueError("Failed to get HEAD^ hash")


def will_commits_be_signed() -> bool:
    result = subprocess.run(
        ["git", "config", "commit.gpgSign"],
        stdout=subprocess.PIPE,
        check=False,
    )
    return result.returncode == 0 and result.stdout.decode("utf-8").strip() == "true"


def run_commit_tree(
    tree_hash: str, content: str, timestamp: str, head_hash: Optional[str]
) -> str:
    args = ["git", "commit-tree", tree_hash, "-m", content]
    if head_hash:
        args.extend(["-p", head_hash])
    if will_commits_be_signed():
        args.append("-S")
    result = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        env=create_git_env(timestamp),
        check=True,
    )
    return result.stdout.decode("utf-8").strip()
