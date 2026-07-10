#!/usr/bin/env bash name=vst3/extras/fetch-deps.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPS_DIR="$ROOT_DIR/deps"

mkdir -p "$DEPS_DIR"
cd "$DEPS_DIR"

# Fetch JUCE if not already present
if [ ! -d "juce" ]; then
  echo "Cloning JUCE..."
  git clone --depth 1 https://github.com/juce-framework/JUCE.git juce
else
  echo "JUCE already present"
fi

# Fetch Steinberg VST3 SDK if not present
if [ ! -d "vst3sdk" ]; then
  echo "Cloning VST3 SDK..."
  git clone --depth 1 https://github.com/steinbergmedia/vst3sdk.git vst3sdk
else
  echo "VST3 SDK already present"
fi

echo "Dependencies are ready in $DEPS_DIR"
