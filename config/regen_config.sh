#!/bin/bash
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$HERE"

./j2cli/j2cli.py --config config.yaml --plugins-dir=j2cli/plugins --template ./config.cmake.jinja -o config.cmake
./j2cli/j2cli.py --config config.yaml --plugins-dir=j2cli/plugins --template ./config.h.in.jinja -o config.h.in
