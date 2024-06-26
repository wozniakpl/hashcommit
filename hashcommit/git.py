import os
import subprocess
from typing import Dict, Optional

from .utils import run_subprocess


def is_in_git_repo() -> bool:
    return (
        run_subprocess(
            ["git", "rev-parse", "--is-inside-work-tree"], check=False
        ).returncode
        == 0
    )


def does_repo_have_any_commits() -> bool:
    return run_subprocess(["git", "rev-parse", "HEAD"], check=False).returncode == 0


def extract_stdout(result: subprocess.CompletedProcess) -> str:
    return str(result.stdout.decode().strip())


def create_git_env(
    timestamp: str, preserve_author: bool, related_commit_hash: Optional[str]
) -> Dict[str, str]:
    env = os.environ.copy()

    if does_repo_have_any_commits():
        args = ["git", "show", "-s", "--format=%ad"]
        if related_commit_hash:
            args.append(related_commit_hash)
        result = run_subprocess(args)
        author_date = extract_stdout(result)
    else:
        author_date = timestamp

    if preserve_author:
        env.pop("GIT_AUTHOR_NAME", None)
        env.pop("GIT_AUTHOR_EMAIL", None)
        env.pop("GIT_COMMITTER_NAME", None)
        env.pop("GIT_COMMITTER_EMAIL", None)

        args = ["git", "show", "-s", "--format=%an|%ae|%cn|%ce"]
        if related_commit_hash:
            args.append(related_commit_hash)
        result = run_subprocess(args)

        author_name, author_email, committer_name, committer_email = extract_stdout(
            result
        ).split("|")

        env["GIT_AUTHOR_NAME"] = author_name
        env["GIT_AUTHOR_EMAIL"] = author_email
        env["GIT_COMMITTER_NAME"] = committer_name
        env["GIT_COMMITTER_EMAIL"] = committer_email

    return {
        **env,
        "GIT_AUTHOR_DATE": author_date,
        "GIT_COMMITTER_DATE": timestamp,
    }


def get_tree_hash(commit: Optional[str] = None) -> str:
    args = ["git", "show", "-s", "--format=%T"]
    if commit:
        args.append(commit)
        result = run_subprocess(args)
        return extract_stdout(result)

    result = run_subprocess(["git", "write-tree"])
    return extract_stdout(result)


def get_head_hash() -> Optional[str]:
    try:
        result = run_subprocess(["git", "rev-parse", "HEAD"])
        return extract_stdout(result)
    except subprocess.CalledProcessError:
        return None


def get_parent_head_hash() -> Optional[str]:
    try:
        result = run_subprocess(["git", "rev-parse", "HEAD^"])
        value = extract_stdout(result)
        if not value:
            raise ValueError("Empty HEAD^ hash")
        return value
    except subprocess.CalledProcessError:
        return None


def will_commits_be_signed() -> bool:
    result = run_subprocess(["git", "config", "commit.gpgSign"], check=False)
    return result.returncode == 0 and extract_stdout(result) == "true"


def run_commit_tree(
    tree_hash: str,
    content: str,
    timestamp: str,
    head_hash: Optional[str],
    preserve_author: bool,
    related_commit_hash: Optional[str],
) -> str:
    args = ["git", "commit-tree", tree_hash, "-m", content]
    if head_hash:
        args.extend(["-p", head_hash])
    if will_commits_be_signed():
        args.append("-S")
    result = run_subprocess(
        args,
        env=create_git_env(
            timestamp=timestamp,
            preserve_author=preserve_author,
            related_commit_hash=related_commit_hash,
        ),
    )
    return extract_stdout(result)
