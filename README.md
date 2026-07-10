# Spider Patcher

A simple, single-file Python app for visually chaining together plugins into a patch, then exporting the result as a `.spdr` file.

## Requirements

- Python 3.8+
- `tkinter` (included with most Python installs; on Ubuntu/Debian if missing: `sudo apt-get install python3-tk`)

No other dependencies — nothing to `pip install`.

## Running it

```bash
python3 spider_patcher.py
```

## Using the app

- **Add a plugin** — pick a type from the dropdown (Gain, EQ, Reverb, Delay, Compressor, Distortion, Chorus, Filter, Limiter, Custom) and click **+ Add**, or just double-click anywhere on the empty canvas.
- **Chain plugins together** — click and drag from a node's green dot (output, right side) to another node's yellow dot (input, left side). A cyan wire appears connecting them.
- **Move a plugin** — click and drag its body.
- **Edit a plugin** — double-click it to rename it and change its parameters.
- **Delete a plugin or wire** — select a node and press `Delete`/`Backspace`, or right-click a node or wire for a context menu.
- **Name your patch** — type a name in the "Patch name" box in the toolbar.
- **Export** — click **Export .spdr** to save the whole patch (all plugins, their parameters, positions, and how they're wired together) as a `.spdr` file.
- **Reopen a patch** — click **Open .spdr** to load a previously exported file back onto the canvas.

## Third-party plugins

Spider Patcher supports installing extra plugins from a local `plugins/`
folder (created next to `spider_patcher.py` the first time you run the app).
No server, account, or internet connection needed.

- Click **Plugins Folder** in the toolbar to open it.
- Drop in a `.spdrplugin` (or `.json`) file — this is a small, safe JSON file
  describing the plugin's name, default parameters, and color. The app never
  executes code from these files.
- Click **Reload Plugins** and the new plugin appears in the "Add plugin"
  dropdown, marked **★ 3rd-party**.
- Two example plugins (Ping Pong Delay, Tape Saturator) ship in the
  `plugins/` folder so you can see it working immediately.
- "Hosting" a plugin for others is as simple as sending them the file — email,
  a shared drive, a repo, however you like — they drop it in their own
  `plugins/` folder and reload.
- If you open a `.spdr` patch that uses a plugin type you don't have
  installed, the node still loads (shown dashed/gray, labeled "missing") with
  its saved parameters intact — install the matching `.spdrplugin` file and
  reload to restore full editing.

See `plugins/README.md` for the exact file format.

## The .spdr file format

A `.spdr` file is plain JSON, so it's easy to read, version-control, or process with other tools:

```json
{
  "format": "spider-patch",
  "version": 1,
  "name": "My Patch",
  "nodes": [
    { "id": 1, "type": "Gain", "name": "Gain", "x": 60, "y": 60, "params": { "Gain (dB)": 0.0 } },
    { "id": 2, "type": "Reverb", "name": "Room Verb", "x": 300, "y": 60, "params": { "Mix (%)": 30, "Decay (s)": 2.0, "Room Size (%)": 50 } }
  ],
  "connections": [
    { "from": 1, "to": 2 }
  ]
}
```
