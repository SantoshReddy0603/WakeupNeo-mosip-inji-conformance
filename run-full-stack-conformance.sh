#!/usr/bin/env bash
# Run the combined official plans through run-conformance.sh.
# Flags: forwards --parallel, --reports-dir and other runner options after --combined.
# Prerequisites: the same configured services, Python, browser and native API rigs
# as run-conformance.sh; run python runner/setup.py before local checks.
# Exit: propagates the main wrapper status; nonzero includes a rejected release gate.
#
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
exec bash ./run-conformance.sh --combined "$@"
