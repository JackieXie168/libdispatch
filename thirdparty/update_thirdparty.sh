#!/usr/bin/env bash
set -eu -o pipefail -o errtrace

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

cd "$SCRIPT_DIR/.."

add_or_update() {
    if [[ -d "thirdparty/$1" ]]; then
        cmd=pull
    else
        cmd=add
    fi
    git subtree "$cmd" --squash -P "thirdparty/$1" "https://github.com/nickhutchinson/$1.git" dispatch
}

add_or_update libpthread_workqueue
add_or_update libBlocksRuntime
add_or_update libkqueue
