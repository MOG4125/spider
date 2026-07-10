#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"

class SpiderEditor  : public juce::AudioProcessorEditor,
                      public juce::Button::Listener
{
public:
    SpiderEditor (SpiderProcessor&);
    ~SpiderEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;

    void buttonClicked(juce::Button* b) override;

private:
    SpiderProcessor& processor;
    juce::TextButton loadPluginButton {"Load Plugin..."};
    juce::TextButton savePatchButton {"Export .spdr"};
    juce::TextButton openPatchButton {"Open .spdr"};

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SpiderEditor)
};
