import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from .args import HashCommitArgs, parse_args
from .version import VERSION


def configure_logging(verbosity: int) -> None:
    log_level = logging.WARNING
    format_str = "[%(levelname)s] [%(asctime)s] %(message)s"
    if verbosity == 1:
        log_level = logging.INFO
    elif verbosity >= 2:
        log_level = logging.DEBUG
        format_str = "[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)d] [%(funcName)s] %(message)s"

    logging.basicConfig(
        format=format_str,
        level=log_level,
    )


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
    logging.debug("Checking if the repository has any commits")
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


def create_a_commit(message: str, timestamp: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "commit", "--allow-empty", "-m", message],
        env=create_git_env(timestamp),
        check=True,
    )


def create_commit_content(message: Optional[str], number: int) -> str:
    return f"""\
{message or ''}

--- meta: {number} ---
""".strip()


def get_tree_hash() -> str:
    result = subprocess.run(
        ["git", "write-tree"],
        stdout=subprocess.PIPE,
        check=True,
    )
    return result.stdout.decode("utf-8").strip()


def get_head_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            check=True,
        )
        value = result.stdout.decode("utf-8").strip()
        if not value:
            raise ValueError("Empty HEAD hash")
        return value
    except subprocess.CalledProcessError:
        raise ValueError("Failed to get HEAD hash")


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


def get_commit_hash(
    content: str, timestamp: str, tree_hash: str, head_hash: str
) -> str:
    if not head_hash:
        raise NotImplementedError("Handling empty repositories is not implemented yet")
    args = ["git", "commit-tree", tree_hash, "-m", content, "-p", head_hash]
    if will_commits_be_signed():
        args.append("-S")
    result = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        env=create_git_env(timestamp),
        check=True,
    )
    return result.stdout.decode("utf-8").strip()


def will_commits_be_signed() -> bool:
    result = subprocess.run(
        ["git", "config", "commit.gpgSign"],
        stdout=subprocess.PIPE,
        check=False,
    )
    return result.returncode == 0 and result.stdout.decode("utf-8").strip() == "true"


def find_commit_content(
    desired_hash: str,
    message: str,
    match_type: str,
    tree_hash: str,
    head_hash: str,
) -> Tuple[str, str]:

    def compare(value: str) -> bool:
        if match_type == "begin":
            return value.startswith(desired_hash)
        elif match_type == "end":
            return value.endswith(desired_hash)
        elif match_type == "contain":
            return desired_hash in value
        raise ValueError(f"Invalid match type: {match_type}")

    timestamp = datetime.now()
    while True:
        timestamp -= timedelta(seconds=1)
        timestamp_str = timestamp.astimezone().strftime("%a %b %d %H:%M:%S %Y %z")
        content = message
        commit_hash = get_commit_hash(content, timestamp_str, tree_hash, head_hash)

        if compare(commit_hash):
            logging.info(
                f"Found a commit hash that matches the desired hash: {commit_hash} for timestamp: {timestamp_str}"
            )

            return content, timestamp_str


def create_a_commit_with_hash(desired_hash: str, message: str, match_type: str) -> None:
    logging.debug(
        f"Creating the initial commit with the desired hash: {desired_hash} ({match_type})"
    )

    head_hash = get_head_hash()
    tree_hash = get_tree_hash()
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
    logging.debug("Amending the commit with the desired hash")

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
    match_type: str,
) -> None:
    logging.debug(
        f"Overriding the existing commit with the desired hash: {desired_hash} ({match_type})"
    )

    head_hash = get_parent_head_hash()
    tree_hash = get_tree_hash()
    commit_message = message or get_commit_message()
    content, timestamp = find_commit_content(
        desired_hash, commit_message, match_type, tree_hash, head_hash
    )
    amend_a_commit(timestamp, tree_hash, head_hash, content)


def main() -> int:
    args: HashCommitArgs = parse_args()
    configure_logging(args.verbose)
    logging.debug(f"Init: {args}")

    if args.version:
        print(f"hashcommit {VERSION}")
        return 0

    if not args.hash:
        print("Error: --hash argument is required.", file=sys.stderr)
        return 1

    if not is_in_git_repo():
        print("fatal: not a git repository", file=sys.stderr)
        return 1

    try:
        if not does_repo_have_any_commits():
            raise NotImplementedError(
                "Handling empty repositories is not implemented yet"
            )

        if args.overwrite:
            overwrite_a_commit_with_hash(
                args.hash,
                args.message,
                args.match_type,
            )
        else:
            if not args.message:
                print(
                    "Error: --message argument is required if not using --overwrite.",
                    file=sys.stderr,
                )
                return 1
            create_a_commit_with_hash(args.hash, args.message, args.match_type)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        return 3
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
