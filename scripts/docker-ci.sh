#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
docker build -t design-strategies:ci "$ROOT"
docker run --rm design-strategies:ci evaluate-pipeline --profile ci-design-eval