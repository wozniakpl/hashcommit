import logging
import subprocess
import sys
from typing import Optional

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
            ["git", "rev-parse", "--is-inside-work-tree"], check=False
        ).returncode
        == 0
    )


def does_repo_have_any_commits() -> bool:
    return (
        subprocess.run(["git", "rev-list", "--count", "HEAD"], check=False).returncode
        == 0
    )


def get_commit_hash(content: str) -> str:
    # check the hash that the git will produce for a commit with such a content (take into account the commit message, staged files, everything)

    # result = subprocess.run(
    #     ["git", "hash-object", "-t", "commit", "--stdin"],
    #     input=content.encode(),
    #     stdout=subprocess.PIPE,
    #     check=True,
    # )
    # return result.stdout.decode().strip()

    # result = subprocess.run(
    #     ["git", "hash-object", "-w", "--stdin"],
    #     input=content.encode(),
    #     stdout=subprocess.PIPE,
    #     check=True,
    # )
    # return result.stdout.decode().strip()
    return "a"


def create_a_commit(author: str, message: str) -> subprocess.CompletedProcess:  # type: ignore
    return subprocess.run(
        ["git", "commit", "--allow-empty", "-m", message],
        env={"GIT_AUTHOR_NAME": author},
        check=True,
    )


def create_commit_content(message: Optional[str], number: int) -> str:
    return f"""\
{message}

;;; meta: {number} ;;;
"""


def get_git_author() -> str:
    return (
        subprocess.run(
            ["git", "config", "user.name"], stdout=subprocess.PIPE, check=True
        )
        .stdout.decode()
        .strip()
    )


def create_initial_commit_with(
    desired_hash: str, message: Optional[str], match_type: str
) -> None:
    # def compare(value: str) -> bool:
    #     if match_type == "begin":
    #         return desired_hash.startswith(value)
    #     elif match_type == "end":
    #         return desired_hash.endswith(value)
    #     elif match_type == "contain":
    #         return value in desired_hash
    #     raise ValueError(f"Invalid match type: {match_type}")

    # number = 0

    # while True:
    #     number += 1
    #     if message is None:
    #         raise NotImplementedError(
    #             "preserving the original commit message is not implemented yet"
    #         )
    #     content = f"{message}\n;;; meta: {number} ;;;"
    #     commit_hash = get_commit_hash(content)
    #     if compare(commit_hash):
    #         print(f"Found a commit hash that matches the desired hash: {commit_hash}")

    #         break

    author = get_git_author()
    content = create_commit_content(message, number=0)

    create_a_commit(author, content)


def main() -> int:
    args: HashCommitArgs = parse_args()
    configure_logging(args.verbose)

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
            create_initial_commit_with(
                desired_hash=args.hash, message=args.message, match_type=args.match_type
            )
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        return 3
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
