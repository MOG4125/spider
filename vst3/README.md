# Spider VST3

This directory contains a JUCE-based VST3 plugin version of Spider.

What this provides
- A JUCE plugin project (GPL) that implements a node-based patcher UI and can host third-party VST/VST3 plugins using JUCE's plugin hosting APIs.
- CI workflow to build Windows, macOS, and Linux artifacts via GitHub Actions.

How to build locally

1) Fetch dependencies (JUCE and the Steinberg VST3 SDK):

   ./extras/fetch-deps.sh

   This will populate deps/juce and deps/vst3sdk. Alternatively, set the JUCE_DIR and VST3_SDK_PATH CMake variables to point to your local copies.

2) Create a build directory and run CMake:

   mkdir build && cd build
   cmake -DCMAKE_BUILD_TYPE=Release ..
   cmake --build . --config Release

3) Find the built plugin artifact in the build output. Install the .vst3/.dll/.so into your DAW's plugin folder.

Notes & caveats
- Hosting plugins inside a plugin can cause compatibility issues with some third-party plugins and some DAWs. Test target plugins and hosts carefully.
- This project is GPL-licensed via JUCE when built with the JUCE GPL sources.
- CI will attempt to fetch JUCE and the VST3 SDK for building. See .github/workflows/vst3-ci.yml for details.
