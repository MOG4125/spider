import sys
import tkinter as tk # Built-in to Python, no installation needed

def run_test():
    try:
        root = tk.Tk()
        root.title("Validation Test")
        tk.Label(root, text="If you see this window, Python is working!").pack(padx=20, pady=20)
        root.mainloop()
    except Exception as e:
        input(f"Error: {e}")

if __name__ == "__main__":
    run_test()
