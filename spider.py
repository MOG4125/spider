import tkinter as tk
import json

class SpiderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spider Patcher UI")
        self.root.geometry("400x300")
        self.root.configure(bg="#2b2b2b") # Dark theme background

        # Header
        self.label = tk.Label(root, text="Spider Patcher System", 
                              font=("Arial", 16, "bold"), fg="white", bg="#2b2b2b")
        self.label.pack(pady=20)

        # Buttons
        self.btn_toggle = tk.Button(root, text="Toggle Spider Hub", 
                                    width=20, height=2, bg="#4a4a4a", fg="white", 
                                    command=lambda: print("Toggled Hub"))
        self.btn_toggle.pack(pady=10)

        self.btn_export = tk.Button(root, text="Export .spdr Patch", 
                                    width=20, height=2, bg="#007acc", fg="white", 
                                    command=self.export_patch)
        self.btn_export.pack(pady=10)

        # Status Bar
        self.status = tk.Label(root, text="System Ready", 
                               fg="green", bg="#2b2b2b")
        self.status.pack(pady=20)

    def export_patch(self):
        # This creates your .spdr file
        data = {"routing": "spider_hub_active", "version": 1.0}
        with open("my_patch.spdr", "w") as f:
            json.dump(data, f)
        self.status.config(text="Success: Saved my_patch.spdr")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpiderApp(root)
    root.mainloop()
