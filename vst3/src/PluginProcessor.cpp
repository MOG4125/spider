#include "PluginProcessor.h"

SpiderProcessor::SpiderProcessor()
{
    scanFormatManagers();
}

SpiderProcessor::~SpiderProcessor() {}

void SpiderProcessor::scanFormatManagers()
{
    formatManager.addDefaultFormats();
}

void SpiderProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    graph.setPlayConfigDetails(getTotalNumInputChannels(), getTotalNumOutputChannels(), sampleRate, samplesPerBlock);
    graph.prepareToPlay(sampleRate, samplesPerBlock);
}

void SpiderProcessor::releaseResources()
{
    graph.releaseResources();
}

#ifndef JucePlugin_PreferredChannelConfigurations
bool SpiderProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    // accept any layout with at least one input and one output
    return layouts.getMainInputChannelSet() == layouts.getMainOutputChannelSet();
}
#endif

void SpiderProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
    juce::AudioSourceChannelInfo info(&buffer, 0, buffer.getNumSamples());
    // Use the underlying graph to process audio
    juce::AudioBuffer<float> tmpBuffer(buffer.getNumChannels(), buffer.getNumSamples());
    tmpBuffer.makeCopyOf(buffer);
    juce::MidiBuffer midiCopy(midiMessages);
    // Simple approach: let the graph process directly
    graph.processBlock(buffer, midiMessages);
}

juce::AudioProcessorEditor* SpiderProcessor::createEditor() { return new juce::GenericAudioProcessorEditor(*this); }
bool SpiderProcessor::hasEditor() const { return true; }

const juce::String SpiderProcessor::getName() const { return "SpiderVST3"; }

bool SpiderProcessor::acceptsMidi() const { return false; }
bool SpiderProcessor::producesMidi() const { return false; }
bool SpiderProcessor::isMidiEffect() const { return false; }
double SpiderProcessor::getTailLengthSeconds() const { return 0.0; }

int SpiderProcessor::getNumPrograms() { return 1; }
int SpiderProcessor::getCurrentProgram() { return 0; }
void SpiderProcessor::setCurrentProgram (int index) {}
const juce::String SpiderProcessor::getProgramName (int index) { return {}; }
void SpiderProcessor::changeProgramName (int index, const juce::String& newName) {}

void SpiderProcessor::getStateInformation (juce::MemoryBlock& destData) {}
void SpiderProcessor::setStateInformation (const void* data, int sizeInBytes) {}

void SpiderProcessor::addPluginInstance(const juce::File& file)
{
    juce::String errorMessage;
    juce::PluginDescription pd;
    pd.fileOrIdentifier = file.getFullPathName();

    // Try to create plugin instance synchronously (may be slow) — for production use async creation
    if (auto instance = formatManager.createPluginInstance(pd, getSampleRate(), getBlockSize(), errorMessage))
    {
        hostedPlugins.add(instance);
        // Add to graph
        auto node = graph.addNode(instance);
        // Connect node into the graph as suitable (left as todo — graph wiring logic)
    }
    else
    {
        DBG("Failed to create plugin: " << errorMessage);
    }
}
