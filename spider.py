import tkinter as tk
import json

class SpiderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spider Controller")
        self.root.geometry("300x150")
        self.btn = tk.Button(root, text="Open Patcher Canvas", command=self.open_patcher)
        self.btn.pack(pady=50)

    def open_patcher(self):
        win = tk.Toplevel(self.root)
        win.title("Spider Patcher Canvas")
        
        # This is the Patcher Engine
        canvas = tk.Canvas(win, width=600, height=400, bg="#1e1e1e")
        canvas.pack()

        # Draw a "Spider Node"
        node = canvas.create_rectangle(50, 50, 150, 100, fill="#007acc", outline="white")
        text = canvas.create_text(100, 75, text="Spider Hub", fill="white")

        # Make the node draggable
        def move_node(event):
            canvas.coords(node, event.x-50, event.y-25, event.x+50, event.y+25)
            canvas.coords(text, event.x, event.y)
            
        canvas.tag_bind(node, "<B1-Motion>", move_node)
        canvas.tag_bind(text, "<B1-Motion>", move_node)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpiderApp(root)
    root.mainloop()
