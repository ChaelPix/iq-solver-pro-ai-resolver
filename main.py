import tkinter as tk
from tkinter import messagebox
from piece import Piece
from plateau import Plateau

PIECE_COLORS = {
    "red": "red", "orange": "orange", "yellow": "yellow", "lime": "lime",
    "green": "green", "white": "lightblue", "cyan": "cyan", "skyblue": "skyblue",
    "blue": "blue", "purple": "purple", "darkred": "darkred", "pink": "pink"
}

class IQPuzzlerInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("IQ Puzzler Pro Solver")
        self.root.geometry("700x620") 

        self.selected_piece = None
        self.rotation_index = 0

        self.team_label = tk.Label(self.root, text="IA41 Projet - Antoine & Traïan", font=("Arial", 10))
        self.team_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)

        # Plateau
        self.plateau_frame = tk.Frame(self.root)
        self.plateau_frame.grid(row=0, column=0, padx=10, pady=10)
        self.cases = [[None for _ in range(11)] for _ in range(5)]
        self.init_plateau()
        self.plateau = Plateau()

        # pieces
        self.pieces_frame = tk.Frame(self.root)
        self.pieces_frame.grid(row=1, column=0, padx=10, pady=10)
        self.pieces = {}
        self.load_pieces()

        # Boutons
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.rotate_button = tk.Button(self.controls_frame, text="Rotate", command=self.rotate_piece)
        self.rotate_button.grid(row=0, column=0, padx=5)
        self.start_button = tk.Button(self.controls_frame, text="Start", command=self.start_resolution)
        self.start_button.grid(row=0, column=1, padx=5)
        self.reset_button = tk.Button(self.controls_frame, text="Reset Board", command=self.reset_board)
        self.reset_button.grid(row=0, column=2, padx=5)

        # algo info
        self.info_frame = tk.Frame(self.root)
        self.info_frame.grid(row=3, column=0, padx=10, pady=10)
        self.info_label = tk.Label(self.info_frame, text="Informations sur l'algorithme", font=("Arial", 14))
        self.info_label.pack()
        self.info_text = tk.Text(self.info_frame, width=80, height=5, state="disabled")
        self.info_text.pack()
        self.update_info("Détails de l'algorithme et du processus ici...")

        
        self.placed_pieces = {}

    def init_plateau(self):
        """Initialize the game grid in the interface."""
        for i in range(5):
            for j in range(11):
                case = tk.Label(self.plateau_frame, width=4, height=2, borderwidth=1, relief="solid", bg="white")
                case.grid(row=i, column=j)
                case.bind("<Button-1>", lambda e, x=i, y=j: self.handle_grid_click(x, y))
                self.cases[i][j] = case

    def afficher_plateau(self):
        """Update the visual board with the pieces' positions."""
        for i in range(5):
            for j in range(11):
                color = "white"
                for piece_name, (variante, pos) in self.placed_pieces.items():
                    if (i, j) in pos:
                        color = PIECE_COLORS[piece_name]
                self.cases[i][j].configure(bg=color)

    def load_pieces(self):
        """Load pieces definitions into the interface and create preview for each."""
        piece_definitions = [
            ("red", [[1, 1, 1, 1], [0, 0, 0, 1]]),
            ("orange", [[0, 1, 0], [1, 1, 1], [1, 0, 0]]),
            ("yellow", [[1, 1, 1, 1], [0, 1, 0, 0]]),
            ("lime", [[1, 1, 1], [1, 0, 1]]),
            ("green", [[1, 1, 1], [0, 1, 0]]),
            ("white", [[1, 1, 1], [0, 1, 1]]),
            ("cyan", [[0, 1], [1, 1]]),
            ("skyblue", [[1, 1, 1], [1, 0, 0], [1, 0, 0]]),
            ("blue", [[0, 0, 1], [1, 1, 1]]),
            ("purple", [[1, 1, 0], [0, 1, 1], [0, 0, 1]]),
            ("darkred", [[0, 1, 1], [1, 1, 0]]),
            ("pink", [[1, 1, 0, 0], [0, 1, 1, 1]])
        ]

        for idx, (piece_name, shape) in enumerate(piece_definitions):
            self.pieces[piece_name] = Piece(piece_name, shape)
            self.create_piece_button_with_preview(piece_name, idx)

    def create_piece_button_with_preview(self, piece_name, idx):
        """Create a button for each piece with a graphical preview in a 6x2 grid."""
        row, col = divmod(idx, 6)
        frame = tk.Frame(self.pieces_frame)
        frame.grid(row=row, column=col, padx=5, pady=5)

        button = tk.Button(frame, text=piece_name.capitalize(),
                           bg=PIECE_COLORS[piece_name],
                           command=lambda n=piece_name: self.select_piece(n))
        button.pack(side="top")
        self.pieces[piece_name].button = button

        canvas = tk.Canvas(frame, width=60, height=60, bg="white")
        canvas.pack(side="bottom")
        self.pieces[piece_name].preview_canvas = canvas
        self.update_piece_preview(piece_name)

    def update_piece_preview(self, piece_name):
        """Update the graphical preview of the piece with its current rotation."""
        piece = self.pieces[piece_name]
        canvas = piece.preview_canvas
        canvas.delete("all")  

        variante = piece.variantes[self.rotation_index] if self.selected_piece == piece_name else piece.variantes[0]
        color = PIECE_COLORS[piece_name]

        for i, row in enumerate(variante):
            for j, val in enumerate(row):
                if val == 1:
                    x0, y0 = j * 15, i * 15
                    x1, y1 = x0 + 15, y0 + 15
                    canvas.create_rectangle(x0, y0, x1, y1, fill=color)

    def select_piece(self, piece_name):
        """Select a piece and reset its rotation index."""
        if self.selected_piece == piece_name:
            self.deselect_piece()
            return

        self.deselect_piece()
        self.selected_piece = piece_name
        self.rotation_index = 0
        self.pieces[piece_name].button.config(relief="sunken")
        self.update_piece_preview(piece_name)

    def deselect_piece(self):
        """Deselect the current piece."""
        if self.selected_piece:
            self.pieces[self.selected_piece].button.config(relief="raised")
            self.update_piece_preview(self.selected_piece)
            self.selected_piece = None
            self.rotation_index = 0

    def rotate_piece(self):
        """Rotate the selected piece if one is selected and update its preview."""
        if self.selected_piece:
            self.rotation_index = (self.rotation_index + 1) % len(self.pieces[self.selected_piece].variantes)
            self.update_piece_preview(self.selected_piece)

    def handle_grid_click(self, i, j):
        """Handle clicks on the game grid for placement or removal of pieces."""
        if self.selected_piece:
            variante = self.pieces[self.selected_piece].variantes[self.rotation_index]
            if self.plateau.peut_placer(variante, (i, j)):
                self.plateau.placer_piece(self.pieces[self.selected_piece], self.rotation_index, (i, j))
                self.placed_pieces[self.selected_piece] = (variante, [(i + dx, j + dy) for dx, row in enumerate(variante) for dy, val in enumerate(row) if val == 1])
                self.pieces[self.selected_piece].button.config(state="disabled")
                self.deselect_piece()
                self.afficher_plateau()
            else:
                messagebox.showerror("Erreur", "Impossible de placer la pièce ici.")

    def reset_board(self):
        """Clear the board and reset all placed pieces."""
        self.plateau = Plateau()
        self.placed_pieces.clear()
        for piece in self.pieces.values():
            piece.button.config(state="normal")
        self.afficher_plateau()

    def update_info(self, text):
        """Update the info text in the algorithm section."""
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", text)
        self.info_text.config(state="disabled")

    def start_resolution(self):
        """Start the algorithm to solve the puzzle."""
        messagebox.showinfo("Start", "Lancement de l'algorithme de résolution.")
        # Appel à l'algorithme de résolution (à implémenter)


if __name__ == "__main__":
    root = tk.Tk()
    interface = IQPuzzlerInterface(root)
    root.mainloop()
