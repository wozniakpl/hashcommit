#!/bin/bash

set -euo pipefail

current_branch_name=$(git rev-parse --abbrev-ref HEAD)

commits=$(git rev-list --count HEAD)
# TODO make that %02g configurable via arg
for i in $(seq -f "%01g" 1 $commits)
do
    hash=$(git rev-list --reverse HEAD | sed -n ${i}p)
    echo "\$ hashcommit --overwrite --hash $i --commit $hash -vv"
    time hashcommit --overwrite --hash $i --commit $hash -vv
done

current_head=$(git rev-parse HEAD)

git branch $current_branch_name $current_head --force
git checkout $current_branch_name