import logging
import sys

from .args import HashCommitArgs, parse_args
from .commit import create_a_commit_with_hash, overwrite_a_commit_with_hash
from .git import does_repo_have_any_commits, is_in_git_repo
from .logging import configure_logging
from .version import VERSION


def main() -> int:
    args: HashCommitArgs = parse_args()
    configure_logging(args.verbose)
    logging.info(f"Args: {args}")

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
