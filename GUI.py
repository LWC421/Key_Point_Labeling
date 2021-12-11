import tkinter as tk
import tkinter.font as font
from tkinter import filedialog
import os
import natsort

class MainWindow(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        