import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import json
from piece import Piece
from plateau import Plateau
import numpy as np
from algo_x_knuth import AlgorithmX
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap import Style, Window

PIECE_COLORS = {
    "red": "red", "orange": "orange", "yellow": "yellow", "lime": "lime",
    "green": "green", "white": "lightblue", "cyan": "cyan", "skyblue": "skyblue",
    "blue": "blue", "purple": "purple", "darkred": "darkred", "pink": "pink", "gray": "gray12", "magenta": "magenta2"
}

class IQPuzzlerInterface:
    def __init__(self, root):
        self.version = 2
        self.root = root
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.grid_x = 12
        self.grid_y = 6
        self.root.title("IQ Puzzler Pro Solver")
        self.root.geometry("870x900") 

        self.selected_piece = None
        self.rotation_index = 0
        self.solution = None
        self.plateau = Plateau()

        self.team_label = tk.Label(self.root, text="IA41 Projet - Antoine & Traïan", font=("Arial", 10))
        self.team_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)

        self.plateau_frame = tk.Frame(self.root)
        self.plateau_frame.grid(row=0, column=0, padx=10, pady=10)
        self.cases = [[None for _ in range(self.grid_x)] for _ in range(self.grid_y)]
        self.init_plateau()

        self.pieces_frame = tk.Frame(self.root)
        self.pieces_frame.grid(row=1, column=0, padx=10, pady=10)
        self.pieces = {}
        self.load_pieces()

        self.controls_frame = ttk.Frame(self.root)
        self.controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Load and Save buttons
        self.load_button = ttk.Button(self.controls_frame, text="Load Board", command=self.charger_plateau)
        self.load_button.grid(row=0, column=0, padx=5)

        self.save_button = ttk.Button(self.controls_frame, text="Save Board", command=self.sauvegarder_plateau)
        self.save_button.grid(row=0, column=1, padx=5)

        # Rotate button
        self.rotate_button = ttk.Button(self.controls_frame, text="Rotate", command=self.rotate_piece, bootstyle="primary")
        self.rotate_button.grid(row=0, column=2, padx=5)

        # Start and Stop buttons
        self.start_button = ttk.Button(self.controls_frame, text="Start", command=self.start_resolution, bootstyle="success")
        self.start_button.grid(row=0, column=3, padx=5)

        self.stop_button = ttk.Button(self.controls_frame, text="Stop", command=self.stop_resolution, bootstyle="danger")
        self.stop_button.grid(row=0, column=4, padx=5)

        # Step navigation buttons
        self.prev_step_button = ttk.Button(self.controls_frame, text="Previous Step", command=self.previous_step, bootstyle="primary")
        self.prev_step_button.grid(row=0, column=5, padx=5)

        self.next_step_button = ttk.Button(self.controls_frame, text="Next Step", command=self.next_step, bootstyle="primary")
        self.next_step_button.grid(row=0, column=6, padx=5)

        # Reset button
        self.reset_button = ttk.Button(self.controls_frame, text="Reset Board", command=self.reset_board, bootstyle="warning")
        self.reset_button.grid(row=0, column=7, padx=5)

        self.h_button = ttk.Button(self.controls_frame, text="Heur. Asc", width=8, command=self.change_heuristic)
        self.h_button.grid(row=1, column=3)
        self.heuristic_ascender = True

        self.info_frame = tk.Frame(self.root)
        self.info_frame.grid(row=3, column=0, padx=10, pady=10)
        self.info_label = tk.Label(self.info_frame, text="Informations sur l'algorithme", font=("Arial", 14))
        self.info_label.pack()
        self.info_text = tk.Text(self.info_frame, width=80, height=5, state="disabled")
        self.info_text.pack()

        self.placed_pieces = {}

        self.solution_steps = []  # Étapes de la solution finale.
        self.current_step = -1  # Indice de l'étape courante.
        self.afficher_plateau()

    def init_plateau(self):
        for i in range(self.grid_y):
            for j in range(self.grid_x):
                case = tk.Label(self.plateau_frame, width=4, height=2, borderwidth=1, relief="solid", bg="white")
                case.grid(row=i, column=j)
                case.bind("<Button-1>", lambda e, x=i, y=j: self.handle_grid_click(x, y))
                case.bind("<Enter>", lambda e, x=i, y=j: self.handle_grid_hover_enter(x, y))
                case.bind("<Leave>", lambda e, x=i, y=j: self.handle_grid_hover_leave(x, y))
                case.bind("<Button-3>", lambda e, x=i, y=j : (self.rotate_piece(), self.afficher_plateau(), self.handle_grid_hover_enter(x, y)))                
                self.cases[i][j] = case

    def handle_grid_hover_enter(self, i, j):
        if self.selected_piece:
            piece = self.pieces[self.selected_piece]
            variante = piece.variantes[self.rotation_index]
            positions = []
            valid_placement = True

            # Calcul des positions et validation
            for dx in range(variante.shape[0]):
                for dy in range(variante.shape[1]):
                    if variante[dx][dy] == 1:
                        x, y = i + dx, j + dy
                        if 0 <= x < self.grid_y and 0 <= y < self.grid_x:
                            if self.plateau.plateau[x][y] == 0:
                                positions.append((x, y))
                            else:
                                valid_placement = False
                        else:
                            valid_placement = False

            # Déterminer la couleur à afficher
            piece_color = PIECE_COLORS.get(self.selected_piece, "gray")
            hover_color = piece_color if valid_placement else "gray"

            # Appliquer la couleur sur les positions
            for x, y in positions:
                self.cases[x][y].configure(bg=hover_color)


    def handle_grid_hover_leave(self, i, j):
        if self.selected_piece:
            # Réinitialiser l'affichage des cases
            self.afficher_plateau()

    def afficher_plateau(self):
        for i in range(self.grid_y):
            for j in range(self.grid_x):
                color = "white"
                for piece_name, data in self.placed_pieces.items():
                    positions = data['positions']
                    if (i, j) in positions:
                        color = PIECE_COLORS[piece_name]
                        break
                self.cases[i][j].configure(bg=color)

    def change_heuristic(self):
        self.heuristic_ascender = not self.heuristic_ascender
        if self.heuristic_ascender:
            self.h_button.config(text="Heur. Asc")
        else:
            self.h_button.config(text="Heur. Desc")

    def load_pieces(self):
        if self.version == 1:
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
        else:
            piece_definitions = [
                ("red", [[1, 1, 1, 0], [0, 0, 1, 1]]),
                ("orange", [[0, 1, 0, 0], [1, 1, 1, 1], [0, 0, 0, 1]]),
                ("yellow", [[1, 1, 1, 0], [1, 0, 1, 1]]),
                ("lime", [[1, 1, 1]]),
                ("green", [[1, 0, 0, 0], [1, 1, 1, 1], [1, 0, 0, 0]]),
                ("skyblue", [[1, 1, 1], [1, 0, 0], [1, 0, 0]]),
                ("white", [[1, 1, 1], [0, 1, 1]]),
                ("blue", [[0, 0, 1], [1, 1, 1]]),
                ("purple", [[1, 1, 1], [1, 1, 0], [1, 0, 0]]),
                ("cyan", [[1, 1], [1, 1]]),
                ("darkred", [[1, 1, 1], [1, 1, 1]]),
                ("gray", [[1, 1, 1, 1, 1],[1, 0, 0, 0, 0]]),
                ("magenta", [[1, 1, 1, 1],[0, 1, 1, 0]]),
                ("pink", [[0, 1, 0], [1, 1, 1]]),
            ]
        self.nbrpieces = len(piece_definitions)
        for idx, (piece_name, shape) in enumerate(piece_definitions):
            self.pieces[piece_name] = Piece(piece_name, shape)
            self.create_piece_button_with_preview(piece_name, idx)
        return len(piece_definitions)
    def create_piece_button_with_preview(self, piece_name, idx):
        row, col = divmod(idx, self.nbrpieces // 2)
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
        if self.selected_piece == piece_name:
            self.deselect_piece()
            return

        self.deselect_piece()
        self.selected_piece = piece_name
        self.rotation_index = 0
        self.pieces[piece_name].button.config(relief="sunken")
        self.update_piece_preview(piece_name)

    def deselect_piece(self):
        if self.selected_piece:
            self.pieces[self.selected_piece].button.config(relief="raised")
            self.update_piece_preview(self.selected_piece)
            self.selected_piece = None
            self.rotation_index = 0

    def rotate_piece(self):
        if self.selected_piece:
            self.rotation_index = (self.rotation_index + 1) % len(self.pieces[self.selected_piece].variantes)
            self.update_piece_preview(self.selected_piece)

    def handle_grid_click(self, i, j):
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
        self.plateau = Plateau()
        self.placed_pieces.clear()
        for piece in self.pieces.values():
            piece.button.config(state="normal")
        self.afficher_plateau()

    def update_info(self, text):
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", text)
        self.info_text.config(state="disabled")

    def sauvegarder_plateau(self):
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
        self.solution = []

        fixed_pieces = {}
        for piece_name, info in self.placed_pieces.items():
            fixed_pieces[piece_name] = {
                'variante_index': info['variante_index'],
                'position': info['position']
            }

        plateau_copy = Plateau()
        plateau_copy.plateau = np.copy(self.plateau.plateau)

        self.algo = AlgorithmX(
            plateau_copy,
            self.pieces,
            self.heuristic_ascender, 
            fixed_pieces,             
            update_callback=self.update_stats
        )

        solutions = self.algo.solve()

        if solutions:
            self.solution = solutions[0]
            self.solution_steps = self.algo.get_solution_steps()
            self.current_step = -1  # Réinitialise avant la première étape
        else:
            self.update_info("Aucune solution trouvée.")
            # Préserver les placements initiaux
            self.afficher_plateau()

    def display_current_step(self):
        """
        Affiche le plateau à l'étape courante.
        """
        self.reset_board_visuellement()

        # Afficher les pièces initialement placées
        for piece_name, data in self.placed_pieces.items():
            color = PIECE_COLORS.get(piece_name, "gray")
            for position in data['positions']:
                i, j = position
                self.cases[i][j].configure(bg=color)

        # Appliquer les étapes jusqu'à l'étape courante
        for step in self.solution_steps[:self.current_step + 1]:
            piece = step['piece']
            color = PIECE_COLORS.get(piece.nom, "gray")
            for cell in step['cells_covered']:
                i, j = cell
                self.cases[i][j].configure(bg=color)

    def afficher_solution(self):
        if not self.solution:
            return

        self.reset_board()

        for sol in self.solution:
            piece = sol['piece']
            color = PIECE_COLORS.get(piece.nom, "gray") 
            for cell in sol['cells_covered']:
                i, j = cell
                self.cases[i][j].configure(bg=color)

    def stop_resolution(self):
        """
        Arrête la résolution en cours.
        """
        if hasattr(self, 'algo'):
            self.algo.request_stop()

    def next_step(self):
        """
        Affiche l'étape suivante de la solution.
        """
        if self.solution_steps and self.current_step < len(self.solution_steps) - 1:
            self.current_step += 1
            self.display_current_step()
        else:
            messagebox.showinfo("Info", "C'est la dernière étape.")

    def previous_step(self):
        """
        Affiche l'étape précédente de la solution.
        """
        if self.solution_steps and self.current_step > 0:
            self.current_step -= 1
            self.display_current_step()
        else:
            messagebox.showinfo("Info", "C'est la première étape.")


    def exporter_grille(self):
        print("Grille :")
        print("plateau = [")
        for row in self.plateau.plateau:
            print("    ", row.tolist(), ",")
        print("]")

    def update_stats(self, stats):
        elapsed_time = stats["time"]
        calculs = stats["calculs"]
        placements_testes = stats["placements_testes"]
        branches_explored = stats.get("branches_explored", 0)
        branches_pruned = stats.get("branches_pruned", 0)
        max_recursion_depth = stats.get("max_recursion_depth", 0)
        solution = stats["solution"]

        info_text = (
            f"Temps écoulé: {elapsed_time:.2f} s\n"
            f"Placements testés: {placements_testes}\n"
            f"Branches explorées: {branches_explored}\n"
            f"Branches coupées: {branches_pruned}\n"
            f"Profondeur maximale de récursion: {max_recursion_depth}\n"
        )
        self.update_info(info_text)

        # Vérifier si l'algorithme est toujours en cours
        if not self.algo.stop_requested:
            # Afficher la solution en cours de calcul
            if solution:
                self.reset_board_visuellement()

                # Afficher les pièces initialement placées
                for piece_name, data in self.placed_pieces.items():
                    color = PIECE_COLORS.get(piece_name, "gray")
                    for position in data['positions']:
                        i, j = position
                        self.cases[i][j].configure(bg=color)

                # Afficher les placements actuels
                for sol in solution:
                    piece = sol['piece']
                    color = PIECE_COLORS.get(piece.nom, "gray")
                    for cell in sol['cells_covered']:
                        i, j = cell
                        self.cases[i][j].configure(bg=color)
        else:
            # Ne pas modifier le plateau si l'algorithme est arrêté
            pass

        self.root.update()

    def reset_board_visuellement(self):
        """Efface le plateau et réinitialise toutes les cases visuellement."""
        for i in range(self.grid_y):
            for j in range(self.grid_x):
                self.cases[i][j].configure(bg="white")