import tkinter as tk
from tkinter import colorchooser, simpledialog, messagebox
import json
from ttkbootstrap.constants import *
from ttkbootstrap import Style, Window
import numpy as np
class PieceEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Piece Editor")
        self.grid_size = 5
        self.piece_color = "red"
        self.piece_shape = [[0] * self.grid_size for _ in range(self.grid_size)]

        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(pady=10)

        self.grid_size_label = tk.Label(self.controls_frame, text="Grid Size:")
        self.grid_size_label.grid(row=0, column=0, padx=5)

        self.grid_size_entry = tk.Entry(self.controls_frame, width=5)
        self.grid_size_entry.grid(row=0, column=1, padx=5)
        self.grid_size_entry.insert(0, str(self.grid_size))

        self.update_grid_button = tk.Button(self.controls_frame, text="Update Grid", command=self.update_grid)
        self.update_grid_button.grid(row=0, column=2, padx=5)

        self.color_button = tk.Button(self.controls_frame, text="Choose Color", command=self.choose_color)
        self.color_button.grid(row=0, column=3, padx=5)

        self.save_button = tk.Button(self.controls_frame, text="Save Piece", command=self.save_piece)
        self.save_button.grid(row=0, column=4, padx=5)

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(pady=10)
        self.init_grid()

    def init_grid(self):
        self.canvas_frame.destroy()
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(pady=10)
        self.canvas = tk.Canvas(self.canvas_frame, width=self.grid_size * 30, height=self.grid_size * 30)
        self.canvas.pack()
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                color = self.piece_color if self.piece_shape[i][j] == 1 else "white"
                rect_id = self.canvas.create_rectangle(j * 30, i * 30, (j + 1) * 30, (i + 1) * 30, fill=color, outline="black")
                self.canvas.tag_bind(rect_id, "<Button-1>", lambda e, x=i, y=j: self.add_block(x, y))
                self.canvas.tag_bind(rect_id, "<Button-3>", lambda e, x=i, y=j: self.remove_block(x, y))

    def update_grid(self):
        try:
            new_size = int(self.grid_size_entry.get())
            if new_size > 0:
                self.grid_size = new_size
                self.piece_shape = [[0] * self.grid_size for _ in range(self.grid_size)]
                self.init_grid()
        except ValueError:
            pass

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose color")
        if color_code:
            self.piece_color = color_code[1]
            self.draw_grid()

    def add_block(self, i, j):
        self.piece_shape[i][j] = 1
        self.draw_grid()

    def remove_block(self, i, j):
        self.piece_shape[i][j] = 0
        self.draw_grid()

    def save_piece(self):
        piece = self.reduce_shape(self.piece_shape.copy())
        piece_definition = f'("color", {piece})\n'
        with open(f"pieces.txt", "a") as f:
            f.write(piece_definition)
        messagebox.showinfo("Saved", f"Piece saved successfully.")
    
    def reduce_shape(self, shape):
        matricenp = np.array(shape)
        lignesnonvides = ~np.all(matricenp == 0, axis = 1)
        colonnesnonvides = ~np.all(matricenp == 0, axis = 0)
        matricereduite = matricenp[lignesnonvides][:, colonnesnonvides]
        return matricereduite.tolist()

root = Window(themename="darkly")
editor = PieceEditor(root)
root.mainloop()
