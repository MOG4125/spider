#!/usr/bin/env python3
"""
Spider Patcher
==============
A simple, self-contained node-based patching app. Add "plugin" nodes to a
canvas, drag between their ports to chain them together into a signal path,
tweak parameters, and export the whole patch as a .spdr file.

Run it with:
    python3 spider_patcher.py

No third-party dependencies are required — everything here is built on
Python's standard library (tkinter).
"""

import json
import os
import random
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "Spider Patcher"
NODE_W = 150
NODE_H = 64
PORT_R = 7

# Third-party plugins live here as data files (never executable code) — drop
# a .spdrplugin (or .json) file in this folder and it's picked up automatically.
PLUGINS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
DEFAULT_THIRD_PARTY_COLOR = "#AB47BC"

PLUGIN_LIBRARY = {
    "Gain":       {"Gain (dB)": 0.0},
    "EQ":         {"Low (dB)": 0.0, "Mid (dB)": 0.0, "High (dB)": 0.0},
    "Reverb":     {"Mix (%)": 30, "Decay (s)": 2.0, "Room Size (%)": 50},
    "Delay":      {"Time (ms)": 250, "Feedback (%)": 30, "Mix (%)": 25},
    "Compressor": {"Threshold (dB)": -20, "Ratio": 4, "Attack (ms)": 10, "Release (ms)": 100},
    "Distortion": {"Drive (%)": 50, "Tone (%)": 50},
    "Chorus":     {"Rate (Hz)": 1.5, "Depth (%)": 30, "Mix (%)": 30},
    "Filter":     {"Cutoff (Hz)": 1000, "Resonance (%)": 10},
    "Limiter":    {"Ceiling (dB)": -0.3, "Release (ms)": 50},
    "Custom":     {},
}

PLUGIN_COLORS = {
    "Gain": "#5C6BC0", "EQ": "#26A69A", "Reverb": "#7E57C2", "Delay": "#EF5350",
    "Compressor": "#FFA726", "Distortion": "#EC407A", "Chorus": "#66BB6A",
    "Filter": "#42A5F5", "Limiter": "#8D6E63", "Custom": "#78909C",
}


class Node:
    """A single plugin block on the canvas."""
    _next_id = 1

    def __init__(self, ptype, x, y, name=None, params=None, source="builtin"):
        self.id = Node._next_id
        Node._next_id += 1
        self.type = ptype
        self.name = name or ptype
        self.x = x
        self.y = y
        self.w = NODE_W
        self.h = NODE_H
        self.params = dict(params) if params else dict(PLUGIN_LIBRARY.get(ptype, {}))
        self.source = source  # "builtin" | "third-party" | "missing"
        # canvas item ids (filled in when drawn)
        self.rect_id = None
        self.title_id = None
        self.type_id = None
        self.in_port_id = None
        self.out_port_id = None

    def in_port_pos(self):
        return self.x, self.y + self.h / 2

    def out_port_pos(self):
        return self.x + self.w, self.y + self.h / 2

    def to_dict(self):
        return {
            "id": self.id, "type": self.type, "name": self.name,
            "x": self.x, "y": self.y, "params": self.params,
        }


class Connection:
    """A wire linking one node's output to another node's input."""

    def __init__(self, from_id, to_id):
        self.from_id = from_id
        self.to_id = to_id
        self.line_id = None

    def to_dict(self):
        return {"from": self.from_id, "to": self.to_id}


class SpiderPatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1100x700")
        self.root.minsize(800, 500)

        self.nodes = {}          # id -> Node
        self.connections = []    # list[Connection]
        self.patch_name = tk.StringVar(value="Untitled Patch")
        self.current_file = None

        self.selected_node_id = None
        self.connecting_from = None
        self.temp_line_id = None
        self.drag_offset = (0, 0)

        self.load_plugins(silent=True)
        self._build_ui()

    # ------------------------------------------------------- Plugin loading
    def load_plugins(self, silent=False):
        """(Re)scan the local plugins/ folder and merge any third-party
        plugin definitions on top of the built-in library. Plugin files are
        plain JSON data (never executable code), so dropping one in is safe.
        """
        self.plugin_params = dict(PLUGIN_LIBRARY)
        self.plugin_colors = dict(PLUGIN_COLORS)
        self.plugin_sources = {t: "builtin" for t in PLUGIN_LIBRARY}
        self.plugin_meta = {}

        os.makedirs(PLUGINS_DIR, exist_ok=True)
        errors = []
        loaded = 0
        for fname in sorted(os.listdir(PLUGINS_DIR)):
            if not (fname.endswith(".spdrplugin") or fname.endswith(".json")):
                continue
            path = os.path.join(PLUGINS_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                ptype = data.get("type")
                if not ptype or not isinstance(ptype, str):
                    raise ValueError("missing required 'type' field")
                params = data.get("params", {})
                if not isinstance(params, dict):
                    raise ValueError("'params' must be an object of name -> default value")
                color = data.get("color", DEFAULT_THIRD_PARTY_COLOR)
                if not (isinstance(color, str) and color.startswith("#")):
                    color = DEFAULT_THIRD_PARTY_COLOR
                self.plugin_params[ptype] = params
                self.plugin_colors[ptype] = color
                self.plugin_sources[ptype] = "third-party"
                self.plugin_meta[ptype] = {
                    "author": str(data.get("author", "Unknown")),
                    "description": str(data.get("description", "")),
                    "file": fname,
                }
                loaded += 1
            except (OSError, ValueError, json.JSONDecodeError) as e:
                errors.append(f"{fname}: {e}")

        if not silent and errors:
            messagebox.showwarning(
                APP_TITLE, "Some plugin files couldn't be loaded:\n\n" + "\n".join(errors))
        return loaded, errors

    def _display_label(self, ptype):
        if self.plugin_sources.get(ptype) == "third-party":
            return f"{ptype}  \u2605 3rd-party"
        return ptype

    def _type_from_label(self, label):
        return label.split("  \u2605")[0] if "  \u2605" in label else label

    def _combo_values(self):
        builtin = [t for t in PLUGIN_LIBRARY if t in self.plugin_params]
        third_party = sorted(t for t, src in self.plugin_sources.items() if src == "third-party")
        return [self._display_label(t) for t in builtin] + [self._display_label(t) for t in third_party]

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        toolbar = ttk.Frame(self.root, padding=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="New", command=self.new_patch).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Open .spdr", command=self.open_patch).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export .spdr", command=self.export_patch).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Label(toolbar, text="Add plugin:").pack(side=tk.LEFT, padx=(0, 4))
        self.plugin_choice = tk.StringVar(value=self._display_label("Gain"))
        self.plugin_menu = ttk.Combobox(
            toolbar, textvariable=self.plugin_choice,
            values=self._combo_values(), state="readonly", width=18)
        self.plugin_menu.pack(side=tk.LEFT)
        ttk.Button(toolbar, text="+ Add", command=self.add_plugin_from_menu).pack(side=tk.LEFT, padx=4)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Button(toolbar, text="Reload Plugins", command=self.reload_plugins).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Plugins Folder", command=self.open_plugins_folder).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Label(toolbar, text="Patch name:").pack(side=tk.LEFT)
        ttk.Entry(toolbar, textvariable=self.patch_name, width=20).pack(side=tk.LEFT, padx=4)

        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="#1e1f26", highlightthickness=0)
        hbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set,
                               scrollregion=(0, 0, 3000, 3000))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<Button-1>", self._on_canvas_click_bg)
        self.canvas.bind("<Double-Button-1>", self._on_canvas_double_click_bg)

        self.root.bind("<Delete>", self._on_delete_key)
        self.root.bind("<BackSpace>", self._on_delete_key)

        self.status = tk.StringVar(
            value="Drag from a node's green (output) dot to another node's yellow (input) dot to chain "
                  "them. Double-click a node to edit it. Double-click empty space to drop a new plugin.")
        status_bar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor="w", padding=4)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ------------------------------------------------------------ Node CRUD
    def reload_plugins(self):
        current_label = self.plugin_choice.get()
        self.load_plugins(silent=True)
        values = self._combo_values()
        self.plugin_menu["values"] = values
        if current_label not in values:
            self.plugin_choice.set(self._display_label("Gain"))
        third_party_count = sum(1 for s in self.plugin_sources.values() if s == "third-party")
        self.status.set(f"Loaded {third_party_count} third-party plugin(s) from {PLUGINS_DIR}")

    def open_plugins_folder(self):
        os.makedirs(PLUGINS_DIR, exist_ok=True)
        try:
            if sys.platform.startswith("win"):
                os.startfile(PLUGINS_DIR)  # noqa: S606 (Windows-only helper)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", PLUGINS_DIR])
            else:
                subprocess.Popen(["xdg-open", PLUGINS_DIR])
        except OSError:
            pass
        messagebox.showinfo(
            APP_TITLE,
            f"Plugins folder:\n{PLUGINS_DIR}\n\n"
            "Drop a .spdrplugin (or .json) file in there, then click "
            "'Reload Plugins' to add it to the dropdown.")

    def add_plugin_from_menu(self):
        ptype = self._type_from_label(self.plugin_choice.get())
        x = 60 + random.randint(0, 5) * 20
        y = 60 + random.randint(0, 10) * 40
        self.add_node(ptype, x, y)

    def add_node(self, ptype, x, y):
        source = self.plugin_sources.get(ptype, "missing")
        params = self.plugin_params.get(ptype)
        node = Node(ptype, x, y, params=params, source=source)
        self.nodes[node.id] = node
        self._draw_node(node)
        label = "third-party " if source == "third-party" else ""
        self.status.set(f"Added {label}plugin '{ptype}'. Drag its ports to chain it to other plugins.")
        return node

    def _draw_node(self, node):
        if node.source == "missing":
            color = "#555555"
        else:
            color = self.plugin_colors.get(node.type, DEFAULT_THIRD_PARTY_COLOR)
        tag = f"node_{node.id}"
        x, y, w, h = node.x, node.y, node.w, node.h

        outline, dash = "#FFFFFF", None
        if node.source == "third-party":
            outline = "#E1BEE7"
        elif node.source == "missing":
            outline, dash = "#FF8A65", (3, 2)

        rect_kwargs = dict(fill=color, outline=outline, width=2, tags=(tag, "draggable", "node_rect"))
        if dash:
            rect_kwargs["dash"] = dash
        node.rect_id = self.canvas.create_rectangle(x, y, x + w, y + h, **rect_kwargs)
        node.title_id = self.canvas.create_text(
            x + w / 2, y + h / 2 - 10, text=node.name, fill="white",
            font=("Segoe UI", 10, "bold"), tags=(tag, "draggable"))
        type_label = node.type
        if node.source == "third-party":
            type_label += "  \u2605"
        elif node.source == "missing":
            type_label += "  (missing)"
        node.type_id = self.canvas.create_text(
            x + w / 2, y + h / 2 + 12, text=type_label, fill="#E0E0E0",
            font=("Segoe UI", 8), tags=(tag, "draggable"))

        ix, iy = node.in_port_pos()
        ox, oy = node.out_port_pos()
        node.in_port_id = self.canvas.create_oval(
            ix - PORT_R, iy - PORT_R, ix + PORT_R, iy + PORT_R,
            fill="#FFEB3B", outline="black", tags=(tag, f"port_in_{node.id}"))
        node.out_port_id = self.canvas.create_oval(
            ox - PORT_R, oy - PORT_R, ox + PORT_R, oy + PORT_R,
            fill="#4CAF50", outline="black", tags=(tag, f"port_out_{node.id}"))

        for item in (node.rect_id, node.title_id, node.type_id):
            self.canvas.tag_bind(item, "<ButtonPress-1>", lambda e, nid=node.id: self._on_node_press(e, nid))
            self.canvas.tag_bind(item, "<B1-Motion>", lambda e, nid=node.id: self._on_node_drag(e, nid))
            self.canvas.tag_bind(item, "<Double-Button-1>", lambda e, nid=node.id: self.edit_node(nid))
            self.canvas.tag_bind(item, "<Button-3>", lambda e, nid=node.id: self._node_context_menu(e, nid))

        self.canvas.tag_bind(node.out_port_id, "<ButtonPress-1>",
                              lambda e, nid=node.id: self._start_connection(nid))
        self.canvas.tag_bind(node.in_port_id, "<ButtonRelease-1>",
                              lambda e, nid=node.id: self._finish_connection(nid))
        self.canvas.tag_bind(node.in_port_id, "<ButtonPress-1>",
                              lambda e, nid=node.id: self._finish_connection(nid))

    def _redraw_node(self, node):
        self.canvas.delete(f"node_{node.id}")
        self._draw_node(node)
        self._redraw_connections_for(node.id)

    def edit_node(self, node_id):
        node = self.nodes.get(node_id)
        if not node:
            return
        dlg = tk.Toplevel(self.root)
        dlg.title(f"Edit {node.type}")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        row = 0
        ttk.Label(dlg, text="Name:").grid(row=row, column=0, sticky="w", padx=8, pady=6)
        name_var = tk.StringVar(value=node.name)
        ttk.Entry(dlg, textvariable=name_var, width=28).grid(row=row, column=1, padx=8, pady=6)
        row += 1

        if node.source == "third-party":
            meta = self.plugin_meta.get(node.type, {})
            info = f"\u2605 Third-party plugin by {meta.get('author', 'Unknown')}"
            if meta.get("description"):
                info += f"\n{meta['description']}"
            ttk.Label(dlg, text=info, foreground="#AB47BC", wraplength=280, justify="left").grid(
                row=row, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 6))
            row += 1
        elif node.source == "missing":
            ttk.Label(
                dlg,
                text="\u26a0 This plugin's definition isn't installed locally. Add the matching\n"
                     ".spdrplugin file to the plugins folder and click 'Reload Plugins'.",
                foreground="#FF8A65", wraplength=280, justify="left").grid(
                row=row, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 6))
            row += 1

        param_vars = {}
        for pname, pval in node.params.items():
            ttk.Label(dlg, text=pname + ":").grid(row=row, column=0, sticky="w", padx=8, pady=4)
            var = tk.StringVar(value=str(pval))
            ttk.Entry(dlg, textvariable=var, width=24).grid(row=row, column=1, padx=8, pady=4)
            param_vars[pname] = var
            row += 1

        def save():
            node.name = name_var.get() or node.type
            for pname, var in param_vars.items():
                raw = var.get()
                try:
                    node.params[pname] = float(raw) if "." in raw else int(raw)
                except ValueError:
                    node.params[pname] = raw
            self._redraw_node(node)
            dlg.destroy()

        btns = ttk.Frame(dlg)
        btns.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Save", command=save).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Delete Plugin",
                   command=lambda: (self.delete_node(node_id), dlg.destroy())).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side=tk.LEFT, padx=6)

    def _node_context_menu(self, event, node_id):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Edit Plugin", command=lambda: self.edit_node(node_id))
        menu.add_command(label="Delete Plugin", command=lambda: self.delete_node(node_id))
        menu.tk_popup(event.x_root, event.y_root)

    def delete_node(self, node_id):
        if node_id not in self.nodes:
            return
        remaining = []
        for c in self.connections:
            if c.from_id == node_id or c.to_id == node_id:
                if c.line_id:
                    self.canvas.delete(c.line_id)
            else:
                remaining.append(c)
        self.connections = remaining
        self.canvas.delete(f"node_{node_id}")
        del self.nodes[node_id]
        if self.selected_node_id == node_id:
            self.selected_node_id = None
        self.status.set("Plugin deleted.")

    # ---------------------------------------------------------------- Drag
    def _on_node_press(self, event, node_id):
        self._select_node(node_id)
        node = self.nodes[node_id]
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        self.drag_offset = (cx - node.x, cy - node.y)

    def _on_node_drag(self, event, node_id):
        node = self.nodes.get(node_id)
        if not node:
            return
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        node.x = cx - self.drag_offset[0]
        node.y = cy - self.drag_offset[1]
        self._redraw_node(node)

    def _select_node(self, node_id):
        if self.selected_node_id and self.selected_node_id in self.nodes:
            old = self.nodes[self.selected_node_id]
            self.canvas.itemconfig(old.rect_id, outline="#FFFFFF", width=2)
        self.selected_node_id = node_id
        node = self.nodes.get(node_id)
        if node:
            self.canvas.itemconfig(node.rect_id, outline="#00E5FF", width=3)

    # --------------------------------------------------------- Connections
    def _start_connection(self, node_id):
        self.connecting_from = node_id
        self.status.set("Drag to a yellow input dot to connect, or click empty space to cancel.")

    def _finish_connection(self, node_id):
        if self.connecting_from is None:
            return
        from_id = self.connecting_from
        self.connecting_from = None
        if self.temp_line_id:
            self.canvas.delete(self.temp_line_id)
            self.temp_line_id = None
        if from_id == node_id:
            return
        for c in self.connections:
            if c.from_id == from_id and c.to_id == node_id:
                return
        conn = Connection(from_id, node_id)
        self._draw_connection(conn)
        self.connections.append(conn)
        self.status.set("Connected! Plugins are now chained together.")

    def _draw_connection(self, conn):
        fn = self.nodes[conn.from_id]
        tn = self.nodes[conn.to_id]
        x1, y1 = fn.out_port_pos()
        x2, y2 = tn.in_port_pos()
        conn.line_id = self.canvas.create_line(
            x1, y1, x2, y2, fill="#00E5FF", width=2, smooth=True,
            arrow=tk.LAST, tags=("connection",))
        self.canvas.tag_lower(conn.line_id)
        self.canvas.tag_bind(conn.line_id, "<Button-3>",
                              lambda e, c=conn: self._connection_context_menu(e, c))

    def _connection_context_menu(self, event, conn):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Delete Connection", command=lambda: self._delete_connection(conn))
        menu.tk_popup(event.x_root, event.y_root)

    def _delete_connection(self, conn):
        if conn.line_id:
            self.canvas.delete(conn.line_id)
        if conn in self.connections:
            self.connections.remove(conn)

    def _redraw_connections_for(self, node_id):
        for c in self.connections:
            if c.from_id == node_id or c.to_id == node_id:
                if c.line_id:
                    self.canvas.delete(c.line_id)
                self._draw_connection(c)

    def _on_canvas_motion(self, event):
        if self.connecting_from is None:
            return
        node = self.nodes.get(self.connecting_from)
        if not node:
            return
        x1, y1 = node.out_port_pos()
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        if self.temp_line_id:
            self.canvas.coords(self.temp_line_id, x1, y1, cx, cy)
        else:
            self.temp_line_id = self.canvas.create_line(
                x1, y1, cx, cy, fill="#00E5FF", width=2, dash=(4, 2))

    def _on_canvas_click_bg(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            if self.connecting_from is not None:
                self.connecting_from = None
                if self.temp_line_id:
                    self.canvas.delete(self.temp_line_id)
                    self.temp_line_id = None
            if self.selected_node_id and self.selected_node_id in self.nodes:
                old = self.nodes[self.selected_node_id]
                self.canvas.itemconfig(old.rect_id, outline="#FFFFFF", width=2)
            self.selected_node_id = None

    def _on_canvas_double_click_bg(self, event):
        if self.canvas.gettags("current"):
            return  # a node handled its own double-click
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        ptype = self.plugin_choice.get()
        self.add_node(ptype, cx - NODE_W / 2, cy - NODE_H / 2)

    def _on_delete_key(self, event):
        if self.selected_node_id:
            self.delete_node(self.selected_node_id)

    # --------------------------------------------------------- File I/O
    def new_patch(self):
        if self.nodes and not messagebox.askyesno("New Patch", "Discard current patch?"):
            return
        self.canvas.delete("all")
        self.nodes.clear()
        self.connections.clear()
        self.selected_node_id = None
        self.connecting_from = None
        self.current_file = None
        self.patch_name.set("Untitled Patch")

    def export_patch(self):
        """Export the current patch as a .spdr (JSON) file."""
        if not self.nodes:
            messagebox.showinfo(APP_TITLE, "Add at least one plugin before exporting.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".spdr",
            filetypes=[("Spider Patch", "*.spdr")],
            initialfile=self._safe_filename(self.patch_name.get()) + ".spdr",
        )
        if not path:
            return
        data = {
            "format": "spider-patch",
            "version": 1,
            "name": self.patch_name.get(),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "connections": [c.to_dict() for c in self.connections],
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.current_file = path
            self.status.set(f"Exported to {os.path.basename(path)}")
            messagebox.showinfo(APP_TITLE, f"Patch exported to:\n{path}")
        except OSError as e:
            messagebox.showerror(APP_TITLE, f"Could not save file:\n{e}")

    def open_patch(self):
        path = filedialog.askopenfilename(filetypes=[("Spider Patch", "*.spdr"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            messagebox.showerror(APP_TITLE, f"Could not open file:\n{e}")
            return

        self.canvas.delete("all")
        self.nodes.clear()
        self.connections.clear()
        self.selected_node_id = None

        id_map = {}
        for nd in data.get("nodes", []):
            ptype = nd.get("type", "Custom")
            source = self.plugin_sources.get(ptype, "missing")
            saved_params = nd.get("params")
            if not saved_params:
                saved_params = self.plugin_params.get(ptype, {})
            node = Node(ptype, nd.get("x", 60), nd.get("y", 60),
                        name=nd.get("name"), params=saved_params, source=source)
            id_map[nd.get("id")] = node.id
            self.nodes[node.id] = node
            self._draw_node(node)

        for c in data.get("connections", []):
            f_old, t_old = c.get("from"), c.get("to")
            if f_old in id_map and t_old in id_map:
                conn = Connection(id_map[f_old], id_map[t_old])
                self._draw_connection(conn)
                self.connections.append(conn)

        missing_types = sorted({n.type for n in self.nodes.values() if n.source == "missing"})
        if missing_types:
            messagebox.showwarning(
                APP_TITLE,
                "This patch uses plugin type(s) that aren't installed locally:\n\n"
                + "\n".join(missing_types) +
                "\n\nInstall the matching .spdrplugin file(s) in the plugins folder, click "
                "'Reload Plugins', then reopen this file to restore full parameter editing.")

        self.patch_name.set(data.get("name", "Untitled Patch"))
        self.current_file = path
        self.status.set(f"Opened {os.path.basename(path)}")

    @staticmethod
    def _safe_filename(name):
        cleaned = "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip()
        return cleaned or "patch"


def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except tk.TclError:
        pass
    SpiderPatcherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
