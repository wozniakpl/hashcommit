import argparse
import sys
from argparse import Namespace
from typing import Optional


class HashCommitArgs(Namespace):
    hash: Optional[str]
    message: Optional[str]
    match_type: str
    version: bool
    verbose: int
    overwrite: bool


def parse_args() -> HashCommitArgs:
    parser = argparse.ArgumentParser(
        description="Generate a Git commit with a specific hash prefix."
    )
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    parser.add_argument("--hash", help="Desired hash string.", type=str)
    parser.add_argument("--message", help="Commit message.", type=str)
    parser.add_argument(
        "--match-type",
        choices=["begin", "contain", "end"],
        default="begin",
        help="Match type.",
    )
    parser.add_argument(
        "--version", action="store_true", help="Show the version of hashcommit."
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity level."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the existing commit instead of creating a new one.",
    )
    return parser.parse_args(namespace=HashCommitArgs())
