import logging
import subprocess
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, Tuple

from .args import MatchType
from .git import (
    create_git_env,
    get_commit_hash,
    get_head_hash,
    get_parent_head_hash,
    get_tree_hash,
    will_commits_be_signed,
)


def create_a_commit(message: str, timestamp: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "commit", "--allow-empty", "-m", message],
        env=create_git_env(timestamp),
        stdout=subprocess.PIPE,
        check=True,
    )


def create_commit_content(message: Optional[str], number: int) -> str:
    return f"""\
{message or ''}

--- meta: {number} ---
""".strip()


def find_commit_content(
    desired_hash: str,
    message: str,
    match_type: MatchType,
    tree_hash: str,
    head_hash: str,
) -> Tuple[str, str]:

    def compare(value: str) -> bool:
        mapping: Dict[MatchType, Callable[[], bool]] = {
            MatchType.BEGIN: lambda: value.startswith(desired_hash),
            MatchType.END: lambda: value.endswith(desired_hash),
            MatchType.CONTAIN: lambda: desired_hash in value,
        }
        return mapping[match_type]()

    timestamp = datetime.now()
    logging.debug(f"Starting from: {timestamp}")
    while True:
        timestamp -= timedelta(seconds=1)
        timestamp_str = timestamp.astimezone().strftime("%a %b %d %H:%M:%S %Y %z")
        content = message
        commit_hash = get_commit_hash(content, timestamp_str, tree_hash, head_hash)

        if compare(commit_hash):
            logging.debug(f"End timestamp: {timestamp}")
            print(f"Found matching commit hash: {commit_hash}")
            return content, timestamp_str


def create_a_commit_with_hash(
    desired_hash: str, message: str, match_type: MatchType
) -> None:
    logging.debug(f"Creating a commit with hash: {desired_hash} ({match_type})")
    head_hash = get_head_hash()
    logging.debug(f"HEAD: {head_hash}")
    tree_hash = get_tree_hash()
    logging.debug(f"Tree: {tree_hash}")
    content, timestamp = find_commit_content(
        desired_hash, message, match_type, tree_hash, head_hash
    )
    create_a_commit(content, timestamp)


def get_commit_message() -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        stdout=subprocess.PIPE,
        check=True,
    )
    return result.stdout.decode("utf-8").strip()


def amend_a_commit(
    timestamp: str, tree_hash: str, parent_hash: str, content: str
) -> None:
    commit_env = create_git_env(timestamp)
    args = ["git", "commit-tree", tree_hash, "-m", content, "-p", parent_hash]
    if will_commits_be_signed():
        args.append("-S")

    result = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        env=commit_env,
        check=True,
    )
    new_commit_hash = result.stdout.decode("utf-8").strip()

    subprocess.run(
        ["git", "reset", "--hard", new_commit_hash],
        check=True,
    )


def overwrite_a_commit_with_hash(
    desired_hash: str,
    message: Optional[str],
    match_type: MatchType,
) -> None:
    logging.debug(f"Overwriting a commit with hash: {desired_hash} ({match_type})")
    head_hash = get_parent_head_hash()
    logging.debug(f"HEAD^: {head_hash}")
    tree_hash = get_tree_hash()
    logging.debug(f"Tree: {tree_hash}")
    commit_message = message or get_commit_message()
    content, timestamp = find_commit_content(
        desired_hash, commit_message, match_type, tree_hash, head_hash
    )
    amend_a_commit(timestamp, tree_hash, head_hash, content)
