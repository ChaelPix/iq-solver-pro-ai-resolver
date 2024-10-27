import tkinter as tk
from tkinter import messagebox
from piece import Piece
from plateau import Plateau
from tkinter import messagebox, filedialog 
import json
PIECE_COLORS = {
    "red": "red", "orange": "orange", "yellow": "yellow", "lime": "lime",
    "green": "green", "white": "lightblue", "cyan": "cyan", "skyblue": "skyblue",
    "blue": "blue", "purple": "purple", "darkred": "darkred", "pink": "pink"
}

class IQPuzzlerInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("IQ Puzzler Pro Solver")
        self.root.geometry("700x720") 

        self.selected_piece = None
        self.rotation_index = 0

        self.team_label = tk.Label(self.root, text="IA41 Projet - Antoine & Traïan", font=("Arial", 10))
        self.team_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)

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
        self.save_button = tk.Button(self.controls_frame, text="Save Board", command=self.sauvegarder_plateau)
        self.save_button.grid(row=0, column=3, padx=5)
        self.load_button = tk.Button(self.controls_frame, text="Load Board", command=self.charger_plateau)
        self.load_button.grid(row=0, column=4, padx=5)

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
        """Initialise la grille du jeu dans l'interface."""
        for i in range(5):
            for j in range(11):
                case = tk.Label(self.plateau_frame, width=4, height=2, borderwidth=1, relief="solid", bg="white")
                case.grid(row=i, column=j)
                case.bind("<Button-1>", lambda e, x=i, y=j: self.handle_grid_click(x, y))
                self.cases[i][j] = case

    def afficher_plateau(self):
        """Met à jour le plateau visuel avec les positions des pièces."""
        for i in range(5):
            for j in range(11):
                color = "white"
                for piece_name, data in self.placed_pieces.items():
                    positions = data['positions']
                    if (i, j) in positions:
                        color = PIECE_COLORS[piece_name]
                        break
                self.cases[i][j].configure(bg=color)

    def load_pieces(self):
        """Charge les définitions des pièces dans l'interface et crée un aperçu pour chacune."""
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
        """Crée un bouton pour chaque pièce avec un aperçu graphique dans une grille 6x2."""
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
        """Met à jour l'aperçu graphique de la pièce avec sa rotation actuelle."""
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
        """Sélectionne une pièce et réinitialise son index de rotation."""
        if self.selected_piece == piece_name:
            self.deselect_piece()
            return

        self.deselect_piece()
        self.selected_piece = piece_name
        self.rotation_index = 0
        self.pieces[piece_name].button.config(relief="sunken")
        self.update_piece_preview(piece_name)

    def deselect_piece(self):
        """Désélectionne la pièce actuelle."""
        if self.selected_piece:
            self.pieces[self.selected_piece].button.config(relief="raised")
            self.update_piece_preview(self.selected_piece)
            self.selected_piece = None
            self.rotation_index = 0

    def rotate_piece(self):
        """Fait pivoter la pièce sélectionnée si une pièce est sélectionnée et met à jour son aperçu."""
        if self.selected_piece:
            self.rotation_index = (self.rotation_index + 1) % len(self.pieces[self.selected_piece].variantes)
            self.update_piece_preview(self.selected_piece)

    def handle_grid_click(self, i, j):
        """Gère les clics sur la grille du jeu pour le placement ou le retrait des pièces."""
        if self.selected_piece:
            piece = self.pieces[self.selected_piece]
            variante = piece.variantes[self.rotation_index]
            if self.plateau.peut_placer(variante, (i, j)):
                self.plateau.placer_piece(piece, self.rotation_index, (i, j))
                positions = [(i + dx, j + dy) for dx, row in enumerate(variante) for dy, val in enumerate(row) if val == 1]
                self.placed_pieces[self.selected_piece] = {
                    'variante_index': self.rotation_index,
                    'position': (i, j),
                    'positions': positions
                }
                piece.button.config(state="disabled")
                self.deselect_piece()
                self.afficher_plateau()
            else:
                messagebox.showerror("Erreur", "Impossible de placer la pièce ici.")
        else:
            for piece_name, data in self.placed_pieces.items():
                if (i, j) in data['positions']:
                    piece = self.pieces[piece_name]
                    self.plateau.retirer_piece(piece, data['variante_index'], data['position'])
                    piece.button.config(state="normal")
                    del self.placed_pieces[piece_name]
                    self.afficher_plateau()
                    break

    def reset_board(self):
        """Efface le plateau et réinitialise toutes les pièces placées."""
        self.plateau = Plateau()
        self.placed_pieces.clear()
        for piece in self.pieces.values():
            piece.button.config(state="normal")
        self.afficher_plateau()

    def update_info(self, text):
        """Met à jour le texte d'information dans la section de l'algorithme."""
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", text)
        self.info_text.config(state="disabled")

    def sauvegarder_plateau(self):
        """Sauvegarde l'état actuel du plateau dans un fichier."""
        fichier = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Fichiers JSON", "*.json")])
        if fichier:
            data = {
                'placed_pieces': {}
            }
            for piece_name, info in self.placed_pieces.items():
                data['placed_pieces'][piece_name] = {
                    'variante_index': info['variante_index'],
                    'position': info['position']
                }
            with open(fichier, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Sauvegarde", "Plateau sauvegardé avec succès.")

    def charger_plateau(self):
        """Charge un état de plateau depuis un fichier."""
        fichier = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")])
        if fichier:
            with open(fichier, 'r') as f:
                data = json.load(f)

            self.reset_board()

            for piece_name, info in data.get('placed_pieces', {}).items():
                if piece_name in self.pieces:
                    piece = self.pieces[piece_name]
                    variante_index = info['variante_index']
                    position = tuple(info['position'])
                    variante = piece.variantes[variante_index]

                    if self.plateau.peut_placer(variante, position):
                        self.plateau.placer_piece(piece, variante_index, position)
                        positions = [(position[0] + dx, position[1] + dy)
                                     for dx, row in enumerate(variante)
                                     for dy, val in enumerate(row) if val == 1]
                        self.placed_pieces[piece_name] = {
                            'variante_index': variante_index,
                            'position': position,
                            'positions': positions
                        }
                        piece.button.config(state="disabled")
                    else:
                        messagebox.showerror("Erreur", f"Impossible de placer la pièce {piece_name} lors du chargement.")
            self.afficher_plateau()
            messagebox.showinfo("Chargement", "Plateau chargé avec succès.")


    def start_resolution(self):
        """Start the algorithm to solve the puzzle."""
        messagebox.showinfo("Start", "Lancement de l'algorithme du GOAT Knuth")
        
        self.exporter_grille()

    def exporter_grille(self):
        print("Grille :")
        print("plateau = [")
        for row in self.plateau.plateau:
            print("    ", row.tolist(), ",")
        print("]")


if __name__ == "__main__":
    root = tk.Tk()
    interface = IQPuzzlerInterface(root)
    root.mainloop()
