cmake_minimum_required(VERSION 3.15)
project(SpiderVST3)

# Allow overriding JUCE_DIR and VST3_SDK via environment or cache
if(NOT DEFINED JUCE_DIR)
  set(JUCE_DIR ${CMAKE_SOURCE_DIR}/deps/juce)
endif()
if(NOT DEFINED VST3_SDK_PATH)
  set(VST3_SDK_PATH ${CMAKE_SOURCE_DIR}/deps/vst3sdk)
endif()

message(STATUS "JUCE_DIR=${JUCE_DIR}")
message(STATUS "VST3_SDK_PATH=${VST3_SDK_PATH}")

add_subdirectory(${JUCE_DIR} juce)

# Inform JUCE about VST3 SDK path
set(JUCE_VST3_SDK_PATH ${VST3_SDK_PATH} CACHE PATH "Path to the Steinberg VST3 SDK")

juce_add_plugin(SpiderVST3
    COMPANY_NAME "Spider"
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    FORMATS VST3
    PRODUCT_NAME "Spider")

target_sources(SpiderVST3 PRIVATE
    src/PluginProcessor.cpp
    src/PluginEditor.cpp
)

target_compile_features(SpiderVST3 PRIVATE cxx_std_17)

# Expose include directories
target_include_directories(SpiderVST3 PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# Link any additional libraries here (none required initially)

# Installation rules (optional)
install(TARGETS SpiderVST3 DESTINATION bin)
