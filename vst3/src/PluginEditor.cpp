#include "PluginEditor.h"

SpiderEditor::SpiderEditor (SpiderProcessor& p) : AudioProcessorEditor (&p), processor (p)
{
    addAndMakeVisible(loadPluginButton);
    loadPluginButton.addListener(this);

    addAndMakeVisible(savePatchButton);
    savePatchButton.addListener(this);

    addAndMakeVisible(openPatchButton);
    openPatchButton.addListener(this);

    setSize (600, 400);
}

SpiderEditor::~SpiderEditor() {}

void SpiderEditor::paint (juce::Graphics& g)
{
    g.fillAll (juce::Colour::fromRGB(30,31,38));
    g.setColour (juce::Colours::white);
    g.setFont (15.0f);
    g.drawFittedText ("Spider VST3 — Node host (preview)", getLocalBounds(), juce::Justification::centredTop, 1);
}

void SpiderEditor::resized()
{
    auto r = getLocalBounds().reduced(12);
    loadPluginButton.setBounds(r.removeFromTop(30));
    r.removeFromTop(8);
    savePatchButton.setBounds(r.removeFromTop(30));
    r.removeFromTop(8);
    openPatchButton.setBounds(r.removeFromTop(30));
}

void SpiderEditor::buttonClicked(juce::Button* b)
{
    if (b == &loadPluginButton)
    {
        juce::FileChooser chooser ("Select a VST or VST3 plugin to load");
        if (chooser.browseForFileToOpen())
        {
            juce::File f = chooser.getResult();
            processor.addPluginInstance(f);
        }
    }
    else if (b == &savePatchButton)
    {
        juce::FileChooser chooser ("Save .spdr patch", juce::File::getSpecialLocation(juce::File::userDocumentsDirectory), "*.spdr");
        if (chooser.browseForFileToSave(true))
        {
            juce::File out = chooser.getResult();
            // Very simple export: write plugin file paths and no detailed params yet
            juce::DynamicObject::Ptr root = new juce::DynamicObject();
            juce::Array<juce::var> nodes;
            for (auto* inst : processor.hostedPlugins)
            {
                juce::DynamicObject::Ptr n = new juce::DynamicObject();
                n->setProperty("type", inst->getName());
                // Not all instances expose file path — skip for now
                nodes.add(juce::var(n));
            }
            root->setProperty("format", "spider-patch");
            root->setProperty("version", 1);
            root->setProperty("nodes", juce::var(nodes));
            juce::var top(root.get());
            out.replaceWithText(juce::JSON::toString(top));
        }
    }
    else if (b == &openPatchButton)
    {
        juce::FileChooser chooser ("Open .spdr patch", juce::File::getSpecialLocation(juce::File::userDocumentsDirectory), "*.spdr");
        if (chooser.browseForFileToOpen())
        {
            juce::File in = chooser.getResult();
            juce::String txt = in.loadFileAsString();
            // Parsing/loading is left as TODO for full fidelity
            juce::AlertWindow::showMessageBoxAsync(juce::AlertWindow::InfoIcon, "Open Patch", "Patch loading is a work-in-progress in this initial build.");
        }
    }
}
