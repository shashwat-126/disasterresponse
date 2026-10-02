#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../ml-service"
python -m app.train
echo "Model training complete. Artifacts updated in ml-service/artifacts/."
