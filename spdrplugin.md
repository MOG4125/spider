# Third-Party Plugins Folder

Drop `.spdrplugin` (or `.json`) files here and click **Reload Plugins** in
the app to add them to the "Add plugin" dropdown. Files are plain JSON —
Spider Patcher never executes code from a plugin file, it just reads the
name, default parameters, and color, so it's safe to share and install
plugin files from other people.

## File format

```json
{
  "type": "My Custom Effect",
  "author": "Your Name",
  "description": "One line about what this plugin does.",
  "color": "#00ACC1",
  "params": {
    "Amount (%)": 50,
    "Rate (Hz)": 1.0
  }
}
```

- `type` (required) — the plugin's name, shown in the dropdown and on the node.
- `params` (required, can be empty `{}`) — parameter names mapped to their
  default values. Values can be numbers or text; users can edit them per-node
  in the app.
- `color` (optional) — a hex color for the node, e.g. `"#7E57C2"`.
- `author` / `description` (optional) — shown in the node's edit dialog.

Two example plugins (`ping_pong_delay.spdrplugin` and
`tape_saturator.spdrplugin`) are included so you can see the format in
action — open the app and you'll see them in the dropdown marked "★
3rd-party".

## Sharing plugins with others

Since a plugin is just a small JSON file, "hosting" one is as simple as
sending someone the `.spdrplugin` file (email, Slack, a shared drive, a
GitHub repo, etc.) — they drop it into their own `plugins/` folder and hit
**Reload Plugins**.
