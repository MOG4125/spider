import tkinter as tk
import json

class SpiderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spider Patcher UI")
        self.root.geometry("400x300")
        self.root.configure(bg="#2b2b2b")

        self.label = tk.Label(root, text="Spider Patcher System", 
                              font=("Arial", 16, "bold"), fg="white", bg="#2b2b2b")
        self.label.pack(pady=20)

        # Updated: Link button to open_patcher function
        self.btn_toggle = tk.Button(root, text="Toggle Spider Hub", 
                                    width=20, height=2, bg="#4a4a4a", fg="white", 
                                    command=self.open_patcher)
        self.btn_toggle.pack(pady=10)

        self.btn_export = tk.Button(root, text="Export .spdr Patch", 
                                    width=20, height=2, bg="#007acc", fg="white", 
                                    command=self.export_patch)
        self.btn_export.pack(pady=10)

    def open_patcher(self):
        # Create a new secondary window
        patcher_win = tk.Toplevel(self.root)
        patcher_win.title("Spider Patcher Canvas")
        patcher_win.geometry("600x400")
        patcher_win.configure(bg="#1e1e1e")
        
        # Add labels or drawing canvas here
        tk.Label(patcher_win, text="Drag & Drop Nodes Here", 
                 fg="white", bg="#1e1e1e").pack(pady=20)

    def export_patch(self):
        data = {"routing": "spider_hub_active"}
        with open("my_patch.spdr", "w") as f:
            json.dump(data, f)
        print("Saved to my_patch.spdr")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpiderApp(root)
    root.mainloop()
