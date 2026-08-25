#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or not in PATH."
  exit 1
fi
echo "Starting Geo Shield AI..."
docker compose up --build
