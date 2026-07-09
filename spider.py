import tkinter as tk

class SpiderPatcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Spider Patcher Canvas")
        self.root.geometry("800x600")
        
        # The Canvas is the main interface
        self.canvas = tk.Canvas(root, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Create a Node
        self.node = self.canvas.create_rectangle(100, 100, 250, 170, 
                                                fill="#2d2d2d", outline="#007acc", width=2)
        self.label = self.canvas.create_text(175, 135, text="Spider Hub", 
                                             fill="white", font=("Arial", 12))

        # Add movement logic
        self.canvas.tag_bind(self.node, "<B1-Motion>", self.move_node)
        self.canvas.tag_bind(self.label, "<B1-Motion>", self.move_node)

    def move_node(self, event):
        # Calculate offset to keep center consistent
        x1, y1, x2, y2 = self.canvas.coords(self.node)
        width = x2 - x1
        height = y2 - y1
        
        self.canvas.coords(self.node, event.x - width/2, event.y - height/2, 
                           event.x + width/2, event.y + height/2)
        self.canvas.coords(self.label, event.x, event.y)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpiderPatcher(root)
    root.mainloop()
