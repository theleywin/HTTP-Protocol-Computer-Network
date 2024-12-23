import tkinter as tk
from tkinter import messagebox, font

class Client_GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("HTTP Client")
        self.window.configure(bg='gray')

    def run(self):
        self.window.mainloop()
        
gui = Client_GUI()
gui.run()