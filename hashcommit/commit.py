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
from .utils import run_subprocess


def create_a_commit(
    message: str, timestamp: str, related_commit_hash: Optional[str]
) -> subprocess.CompletedProcess:
    return run_subprocess(
        ["git", "commit", "--allow-empty", "-m", message],
        env=create_git_env(
            timestamp=timestamp,
            preserve_author=False,
            related_commit_hash=related_commit_hash,
        ),
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
    related_commit_hash: Optional[str],
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
            tree_hash,
            content,
            timestamp_str,
            head_hash,
            preserve_author,
            related_commit_hash,
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
        related_commit_hash=None,
    )
    create_a_commit(message=content, timestamp=timestamp, related_commit_hash=None)


def get_commit_message(commit: Optional[str] = None) -> str:
    args = ["git", "show", "--no-patch", "--format=%B"]
    if commit:
        args.append(commit)
    result = run_subprocess(args)
    return result.stdout.decode("utf-8").strip()


def amend_a_commit(
    timestamp: str,
    tree_hash: str,
    parent_hash: str,
    content: str,
    preserve_author: bool,
    related_commit_hash: str,
) -> None:
    """Amend the last commit with new content."""
    new_commit_hash = run_commit_tree(
        tree_hash=tree_hash,
        content=content,
        timestamp=timestamp,
        head_hash=parent_hash,
        preserve_author=preserve_author,
        related_commit_hash=related_commit_hash,
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
    current_hash = get_head_hash()
    if not current_hash:
        raise ValueError("No commit to overwrite")
    logging.debug(f"HEAD: {current_hash}")
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
        related_commit_hash=current_hash,
    )
    amend_a_commit(
        timestamp=timestamp,
        tree_hash=tree_hash,
        parent_hash=head_hash,
        content=content,
        preserve_author=preserve_author,
        related_commit_hash=current_hash,
    )


def get_parent_hash(commit: Optional[str] = None) -> Optional[str]:
    args = ["git", "show", "--no-patch", "--format=%P"]
    if commit:
        args.append(commit)

    result = run_subprocess(args)
    parents = result.stdout.decode("utf-8").strip().split()
    if len(parents) > 1:
        raise NotImplementedError("Commit has more than one parent")
    return parents[0] if parents else None


def overwrite_and_rebase(
    desired_hash: str,
    message: Optional[str],
    commit_hash: str,
    preserve_author: bool,
    match_type: MatchType,
) -> None:
    logging.debug(
        f"Will overwrite commit {commit_hash} with hash: {desired_hash} ({match_type})"
    )

    parent_hash = get_parent_hash(commit=commit_hash)
    logging.debug(f"Parent: {parent_hash}")
    tree_hash = get_tree_hash(commit=commit_hash)
    logging.debug(f"Tree: {tree_hash}")
    commit_message = message or get_commit_message(commit=commit_hash)
    logging.debug(f"Message: {commit_message}")

    content, timestamp = find_commit_content(
        desired_hash=desired_hash,
        message=commit_message,
        match_type=match_type,
        tree_hash=tree_hash,
        head_hash=parent_hash,
        preserve_author=preserve_author,
        related_commit_hash=commit_hash,
    )
    logging.debug(f"Content: {content}")
    logging.debug(f"Timestamp: {timestamp}")

    new_commit_hash = run_commit_tree(
        tree_hash=tree_hash,
        content=content,
        timestamp=timestamp,
        head_hash=parent_hash,
        preserve_author=preserve_author,
        related_commit_hash=commit_hash,
    )

    logging.debug(f"Replacing {commit_hash} with {new_commit_hash}")
    subprocess.run(["git", "replace", commit_hash, new_commit_hash, "--force"], check=True)

    logging.debug(f"Rebasing onto {new_commit_hash}")
    subprocess.run(
        ["git", "rebase", "--onto", new_commit_hash, commit_hash, "HEAD"], check=True
    )

    logging.debug(f"Deleting {commit_hash} replacement")
    subprocess.run(["git", "replace", "--delete", commit_hash], check=True)
