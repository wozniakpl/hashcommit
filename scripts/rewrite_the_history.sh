#!/bin/bash

# This script should be called from the repository that you want to rewrite the history in.
# It will rewrite the history of the current branch, starting from the first commit.

set -euo pipefail

digits="3"

usage() {
    echo "Usage: $0 [-d digits]"
    echo "  -d digits   Number of digits for the sequence number (default: 3)"
    exit 1
}

while getopts "d:h" opt; do
    case ${opt} in
        d )
            digits=$OPTARG
            ;;
        h )
            usage
            ;;
        \? )
            usage
            ;;
    esac
done

shift $((OPTIND -1))

format="%0${digits}g"

current_branch_name=$(git rev-parse --abbrev-ref HEAD)
commits=$(git rev-list --count HEAD)

for i in $(seq -f "$format" 0 $((commits - 1)))
do
    hash=$(git rev-list --reverse HEAD | sed -n $((i + 1))p)
    command="hashcommit --overwrite --hash $i --commit $hash -vv"
    echo "\$ $command"
    time eval $command
done

current_head=$(git rev-parse HEAD)
git branch $current_branch_name $current_head --force
git checkout $current_branch_name
