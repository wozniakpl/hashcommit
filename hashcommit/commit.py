import logging
import subprocess
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, Tuple

from .args import MatchType
from .git import (
    create_git_env,
    get_head_hash,
    get_parent_head_hash,
    get_tree_hash,
    run_commit_tree,
)


def create_a_commit(message: str, timestamp: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "commit", "--allow-empty", "-m", message],
        env=create_git_env(timestamp, preserve_author=False),
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
    head_hash: Optional[str],
    preserve_author: bool,
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
        commit_hash = run_commit_tree(
            tree_hash, content, timestamp_str, head_hash, preserve_author
        )

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
        desired_hash=desired_hash,
        message=message,
        match_type=match_type,
        tree_hash=tree_hash,
        head_hash=head_hash,
        preserve_author=False,
    )
    create_a_commit(message=content, timestamp=timestamp)


def get_commit_message() -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        stdout=subprocess.PIPE,
        check=True,
    )
    return result.stdout.decode("utf-8").strip()


def amend_a_commit(
    timestamp: str,
    tree_hash: str,
    parent_hash: str,
    content: str,
    preserve_author: bool,
) -> None:
    new_commit_hash = run_commit_tree(
        tree_hash=tree_hash,
        content=content,
        timestamp=timestamp,
        head_hash=parent_hash,
        preserve_author=preserve_author,
    )
    subprocess.run(
        ["git", "reset", "--hard", new_commit_hash],
        check=True,
    )


def overwrite_a_commit_with_hash(
    desired_hash: str,
    message: Optional[str],
    match_type: MatchType,
    preserve_author: bool,
) -> None:
    logging.debug(f"Overwriting a commit with hash: {desired_hash} ({match_type})")
    head_hash = get_parent_head_hash()
    logging.debug(f"HEAD^: {head_hash}")
    tree_hash = get_tree_hash()
    logging.debug(f"Tree: {tree_hash}")
    commit_message = message or get_commit_message()
    content, timestamp = find_commit_content(
        desired_hash=desired_hash,
        message=commit_message,
        match_type=match_type,
        tree_hash=tree_hash,
        head_hash=head_hash,
        preserve_author=preserve_author,
    )
    amend_a_commit(
        timestamp=timestamp,
        tree_hash=tree_hash,
        parent_hash=head_hash,
        content=content,
        preserve_author=preserve_author,
    )
