import tkinter as tk
import json

class SpiderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spider Patcher")
        self.root.geometry("400x300")

        # UI Elements
        self.label = tk.Label(root, text="Spider Patcher Interface", font=("Arial", 14))
        self.label.pack(pady=20)

        self.btn_export = tk.Button(root, text="Export .spdr Patch", command=self.export_patch)
        self.btn_export.pack(pady=10)

        self.status = tk.Label(root, text="Ready")
        self.status.pack(pady=10)

    def export_patch(self):
        # Create dummy patch data
        data = {"status": "active", "nodes": 1}
        with open("my_patch.spdr", "w") as f:
            json.dump(data, f)
        self.status.config(text="Saved: my_patch.spdr")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpiderApp(root)
    root.mainloop()
