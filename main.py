import tkinter as tk
from interface import IQPuzzlerInterface
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap import Style, Window

if __name__ == "__main__":
    root = Window(themename="darkly") 
    interface = IQPuzzlerInterface(root)
    root.mainloop()
