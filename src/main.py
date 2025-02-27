import tkinter as tk
from interface import IQPuzzlerInterface
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap import Style, Window
from cProfile import Profile
from pstats import Stats


def profile_application():
    profiler = Profile()
    profiler.enable()
    root = Window(themename="darkly") 
    interface = IQPuzzlerInterface(root)
    root.mainloop()
    profiler.disable()
    stats = Stats(profiler)
    stats.strip_dirs().sort_stats('cumulative').print_stats(20)
    
if __name__ == "__main__":
    profile_application()
