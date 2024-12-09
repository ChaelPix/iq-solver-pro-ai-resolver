import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import json
import numpy as np
from piece import Piece
from plateau import Plateau
from ttkbootstrap import Style, Window
from ttkbootstrap.constants import *
from solve_manager import SolverManager
from multi_solver_manager import MultiHeuristicManager
import threading

# PIECE_COLORS = {
#     "red": "red", "orange": "orange", "yellow": "yellow", "lime": "lime",
#     "green": "green", "white": "lightblue", "cyan": "cyan", "skyblue": "skyblue",
#     "blue": "blue", "purple": "purple", "darkred": "darkred", "pink": "pink",
#     "gray": "gray12", "magenta": "magenta2"
# }

PIECE_COLORS = {
    "gray1": "gray1",
    "gray2": "gray2",
    "gray3": "gray3",
    "gray4": "gray4",
    "gray5": "gray5",
    "gray6": "gray6",
    "gray7": "gray7",
    "gray8": "gray8",
    "gray9": "gray9",
    "gray10": "gray10",
    "gray11": "gray11",
    "gray12": "gray12",
    "gray13": "gray13",
    "gray14": "gray14",
    "gray15": "gray15",
    "gray16": "gray16",
    "gray17": "gray17",
    "gray18": "gray18",
    "gray19": "gray19",
    "gray20": "gray20",
    "gray21": "gray21",
    "gray22": "gray22",
    "gray23": "gray23",
    "gray24": "gray24",
    "gray25": "gray25",
    "gray26": "gray26",
    "gray27": "gray27",
}


class IQPuzzlerInterface:
    """
    Classe gérant l'interface graphique de l'application IQ Puzzler.
    Elle permet de:
    - Afficher le plateau et ses cellules.
    - Sélectionner et placer des pièces.
    - Charger et sauvegarder l'état du plateau.
    - Lancer la résolution du puzzle via AlgorithmX (via SolverManager).
    - Mettre à jour périodiquement les statistiques et l'état courant.
    - Parcourir les étapes de la solution finale.

    La logique d'interaction avec l'algorithme a été modifiée pour:
    - Utiliser un SolverManager au lieu d'un callback.
    - L'interface lance l'algo (run()), puis dans une boucle (ou via un timer),
      elle appelle get_stats(), get_current_solution_steps() pour rafraîchir l'affichage.
    - Une fois l'algo terminé, on affiche la solution finale.

    Paramètres:
    - root (Tk): Fenêtre racine Tkinter.
    """
    def __init__(self, root):
        self.root = root

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.version = 2
        if(self.version == 1):
            self.grid_x = 11
            self.grid_y = 5
        else:
            self.grid_x = 14
            self.grid_y = 8

        self.root.title("IQ Puzzler Pro Solver")
        self.root.geometry("870x900")

        # Gestion des pièces et plateau
        self.selected_piece = None
        self.rotation_index = 0
        self.solution = None
        self.plateau = Plateau()

        self.team_label = tk.Label(self.root, text="IA41 Projet - Antoine & Traïan", font=("Arial", 10))
        self.team_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)

        # Plateau graphique
        self.plateau_frame = tk.Frame(self.root)
        self.plateau_frame.grid(row=0, column=0, padx=10, pady=10)
        self.cases = [[None for _ in range(self.grid_x)] for _ in range(self.grid_y)]
        self.init_plateau()

        # Chargement des pièces
        self.pieces_frame = tk.Frame(self.root)
        self.pieces_frame.grid(row=1, column=0, padx=10, pady=10)
        self.pieces = {}
        self.load_pieces()

        # Cadre de contrôle (boutons)
        self.controls_frame = ttk.Frame(self.root)
        self.controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Boutons Load/Save
        self.load_button = ttk.Button(self.controls_frame, text="Load Board", command=self.charger_plateau)
        self.load_button.grid(row=0, column=0, padx=5)

        self.save_button = ttk.Button(self.controls_frame, text="Save Board", command=self.sauvegarder_plateau)
        self.save_button.grid(row=0, column=1, padx=5)

        # Bouton rotation
        self.rotate_button = ttk.Button(self.controls_frame, text="Rotate", command=self.rotate_piece, bootstyle="primary")
        self.rotate_button.grid(row=0, column=2, padx=5)

        # Boutons start/stop
        self.start_button = ttk.Button(self.controls_frame, text="Start", command=self.start_resolution, bootstyle="success")
        self.start_button.grid(row=0, column=3, padx=5)
        self.start2_button = ttk.Button(self.controls_frame, text="Start Multithread", command=self.start_resolution_multi, bootstyle="success")
        self.start2_button.grid(row=1, column=5, padx=5)

        self.stop_button = ttk.Button(self.controls_frame, text="Stop", command=self.stop_resolution, bootstyle="danger")
        self.stop_button.grid(row=0, column=4, padx=5)

        # Boutons navigation étape
        self.prev_step_button = ttk.Button(self.controls_frame, text="Previous Step", command=self.previous_step, bootstyle="primary")
        self.prev_step_button.grid(row=0, column=5, padx=5)

        self.next_step_button = ttk.Button(self.controls_frame, text="Next Step", command=self.next_step, bootstyle="primary")
        self.next_step_button.grid(row=0, column=6, padx=5)

        # Reset board
        self.reset_button = ttk.Button(self.controls_frame, text="Reset Board", command=self.reset_board, bootstyle="warning")
        self.reset_button.grid(row=0, column=7, padx=5)

        # Bouton changement heuristique
        self.heuristic_choice = tk.StringVar(value="ascender")
        ttk.OptionMenu(self.controls_frame, self.heuristic_choice, "ascender",
                    "ascender", "descender", 
                    "compactness", "compactness_inverse",
                    "perimeter", "perimeter_inverse",
                    "holes", "holes_inverse").grid(row=1, column=3)

        # Cadre d'information
        self.info_frame = tk.Frame(self.root)
        self.info_frame.grid(row=3, column=0, padx=10, pady=10)
        self.info_label = tk.Label(self.info_frame, text="Informations sur l'algorithme", font=("Arial", 14))
        self.info_label.pack()
        self.info_text = tk.Text(self.info_frame, width=80, height=5, state="disabled")
        self.info_text.pack()

        self.placed_pieces = {}
        self.solution_steps = []
        self.current_step = -1

        self.manager = None
        self.afficher_plateau()

        self.manager_thread = None
        self.is_solving = False  

    def init_plateau(self):
        """
        Initialise l'affichage graphique du plateau (cases).
        Lie les événements de clic et de hover aux cases.
        """
        self.plateau = Plateau(lignes=self.grid_y, colonnes=self.grid_x)
        self.cases = [[None for _ in range(self.grid_x)] for _ in range(self.grid_y)]

        for i in range(self.grid_y):
            for j in range(self.grid_x):
                case = tk.Label(self.plateau_frame, width=2, height=1, borderwidth=1, relief="solid", bg="white")
                case.grid(row=i, column=j)
                case.bind("<Button-1>", lambda e, x=i, y=j: self.handle_grid_click(x, y))
                case.bind("<Enter>", lambda e, x=i, y=j: self.handle_grid_hover_enter(x, y))
                case.bind("<Leave>", lambda e, x=i, y=j: self.handle_grid_hover_leave(x, y))
                case.bind("<Button-3>", lambda e, x=i, y=j : (self.rotate_piece(), self.afficher_plateau(), self.handle_grid_hover_enter(x, y)))                
                self.cases[i][j] = case

    def handle_grid_hover_enter(self, i, j):
        """
        Survol d'une cellule du plateau avec la souris.
        Si une pièce est sélectionnée, on montre une prévisualisation en colorant les cases
        où la pièce pourrait être placée.
        """
        if self.selected_piece:
            piece = self.pieces[self.selected_piece]
            variante = piece.variantes[self.rotation_index]
            positions = []
            valid_placement = True

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

            piece_color = PIECE_COLORS.get(self.selected_piece, "gray")
            hover_color = piece_color if valid_placement else "gray"
            for x, y in positions:
                self.cases[x][y].configure(bg=hover_color)

    def handle_grid_hover_leave(self, i, j):
        """
        Sortie du survol: on réaffiche le plateau tel qu'il était.
        """
        if self.selected_piece:
            self.afficher_plateau()

    def afficher_plateau(self):
        """
        Affiche le plateau en fonction des pièces placées.
        Les cases occupées ont la couleur de la pièce correspondante.
        Les cases vides sont blanches.
        """
        for i in range(self.grid_y):
            for j in range(self.grid_x):
                color = "white"
                for piece_name, data in self.placed_pieces.items():
                    if (i, j) in data['positions']:
                        color = PIECE_COLORS[piece_name]
                        break
                self.cases[i][j].configure(bg=color)

    def change_heuristic(self):
        """
        Inverse le mode d'heuristique (ascendante / descendante)
        et met à jour le texte du bouton.
        """
        self.heuristic_ascender = not self.heuristic_ascender
        if self.heuristic_ascender:
            self.h_button.config(text="Heur. Asc")
        else:
            self.h_button.config(text="Heur. Desc")

    def load_pieces(self):
        """
        Charge la liste des pièces définies (selon version),
        crée les objets Piece et les affiche (boutons + preview).
        """
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
                ("gray1", [
                    [1, 1, 1],
                    [1, 1, 0],
                    [1, 0, 0],
                    [1, 0, 0],
                ]),
                ("gray2", [
                    [0, 1, 1, 1],
                    [1, 1, 1, 0],
                    [0, 1, 0, 0],
                ]),
                ("gray3", [
                    [0, 1, 1, 1],
                    [1, 1, 1, 0],
                ]),
                ("gray4", [
                    [0, 1, 1, 1],
                    [1, 1, 1, 0],
                ]),
                ("gray5", [
                    [0, 1, 1],
                    [1, 1, 1],
                    [0, 1, 1],
                ]),
                ("gray6", [
                    [1],
                    [1],
                ]),
                ("gray7", [
                    [1, 0],
                    [1, 1],
                    [1, 0],
                    [1, 0],
                    [1, 0],
                    [1, 0],
                ]),
                ("gray8", [
                    [1, 1],
                    [1, 1],
                    [1, 0],
                ]),
                ("gray9", [
                    [1],
                    [1],
                ]),
                ("gray10", [
                    [1, 1, 1],
                    [1, 1, 0],
                ]),
                ("gray11", [
                    [1, 1],
                    [1, 1],
                ]),
                ("gray12", [
                    [0, 1, 0],
                    [1, 1, 1],
                    [0, 1, 1],
                ]),
                ("gray13", [
                    [1, 1],
                    [1, 0],
                ]),
                ("gray14", [
                    [1, 1],
                    [1, 1],
                    [1, 1],
                    [1, 1],
                ]),
                ("gray15", [
                    [1, 0, 0],
                    [1, 1, 1],
                    [1, 1, 0],
                    [1, 0, 0],
                ]),
                ("gray16", [
                    [1, 1, 1],
                    [0, 1, 1],
                    [0, 1, 0],
                ]),
                ("gray17", [
                    [1, 0],
                    [1, 1],
                    [1, 0],
                ]),
                ("gray18", [
                    [1],
                    [1],
                ]),
                ("gray19", [
                    [0, 1, 0],
                    [1, 1, 1],
                    [0, 1, 0],
                ]),
                ("gray20", [
                    [0, 1, 0, 0],
                    [1, 1, 1, 1],
                ]),
                ("gray21", [
                    [0, 1, 0, 1, 1],
                    [1, 1, 1, 1, 1],
                ]),
            ]
        self.nbrpieces = len(piece_definitions)
        for idx, (piece_name, shape) in enumerate(piece_definitions):
            self.pieces[piece_name] = Piece(piece_name, shape)
            self.create_piece_button_with_preview(piece_name, idx)
        return len(piece_definitions)

    def create_piece_button_with_preview(self, piece_name, idx):
        """
        Crée un bouton et un aperçu graphique de la pièce.

        Paramètres:
        - piece_name (str): Nom de la pièce.
        - idx (int): Indice pour positionner le bouton dans le grid.
        """
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
        """
        Met à jour l'aperçu d'une pièce (dessinée sur un petit canvas),
        pour montrer sa forme actuelle (en fonction de rotation_index).
        """
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
        """
        Sélectionne une pièce (ou la désélectionne si déjà sélectionnée).
        """
        if self.selected_piece == piece_name:
            self.deselect_piece()
            return

        self.deselect_piece()
        self.selected_piece = piece_name
        self.rotation_index = 0
        self.pieces[piece_name].button.config(relief="sunken")
        self.update_piece_preview(piece_name)

    def deselect_piece(self):
        """
        Désélectionne la pièce courante (si existe).
        """
        if self.selected_piece:
            self.pieces[self.selected_piece].button.config(relief="raised")
            self.update_piece_preview(self.selected_piece)
            self.selected_piece = None
            self.rotation_index = 0

    def rotate_piece(self):
        """
        Fait tourner la pièce sélectionnée, si une pièce est sélectionnée.
        """
        if self.selected_piece:
            self.rotation_index = (self.rotation_index + 1) % len(self.pieces[self.selected_piece].variantes)
            self.update_piece_preview(self.selected_piece)

    def handle_grid_click(self, i, j):
        """
        Gère le clic sur une case du plateau.
        - Si une pièce est sélectionnée, on tente de la placer.
        - Sinon, si on clique sur une case occupée, on retire la pièce.
        """
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
            # Retrait de la pièce si clic sur une pièce déjà placée
            for piece_name, data in self.placed_pieces.items():
                if (i, j) in data['positions']:
                    piece = self.pieces[piece_name]
                    self.plateau.retirer_piece(piece, data['variante_index'], data['position'])
                    piece.button.config(state="normal")
                    del self.placed_pieces[piece_name]
                    self.afficher_plateau()
                    break

    def reset_board(self):
        """
        Réinitialise le plateau et retire toutes les pièces placées.
        """
        self.plateau = Plateau(lignes=self.grid_y, colonnes=self.grid_x)
        self.placed_pieces.clear()
        for piece in self.pieces.values():
            piece.button.config(state="normal")
        self.afficher_plateau()

    def update_info(self, text):
        """
        Met à jour la zone d'information (Text) avec le texte donné.
        """
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", text)
        self.info_text.config(state="disabled")

    def sauvegarder_plateau(self):
        """
        Sauvegarde l'état actuel du plateau (pièces placées) dans un fichier JSON.
        """
        fichier = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Fichiers JSON", "*.json")])
        if fichier:
            data = {'placed_pieces': {}}
            for piece_name, info in self.placed_pieces.items():
                data['placed_pieces'][piece_name] = {
                    'variante_index': info['variante_index'],
                    'position': info['position']
                }
            with open(fichier, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Sauvegarde", "Plateau sauvegardé avec succès.")

    def charger_plateau(self):
        """
        Charge un plateau depuis un fichier JSON.
        """
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
        """
        Lance la résolution du puzzle via le SolverManager.
        Ensuite, met en place un timer pour périodiquement rafraîchir l'affichage des stats
        et afficher la solution une fois que l'algorithme est terminé.
        """
        self.solution = []
        fixed_pieces = {}
        for piece_name, info in self.placed_pieces.items():
            fixed_pieces[piece_name] = {
                'variante_index': info['variante_index'],
                'position': info['position']
            }

        plateau_copy = Plateau()
        plateau_copy.lignes = self.grid_y
        plateau_copy.colonnes = self.grid_x
        plateau_copy.plateau = np.copy(self.plateau.plateau)
        heuristic = self.heuristic_choice.get()
        self.manager = SolverManager(
            plateau_copy,
            self.pieces,
            heuristic,
            fixed_pieces
        )

        self.disable_controls()
        self.is_solving = True

        self.manager_thread = threading.Thread(target=self.manager.run)
        self.manager_thread.start()

        self.update_feedback()

    def update_feedback(self):
        """
        Mise à jour continue de l'interface pendant que la résolution est en cours.
        Appelée périodiquement via `self.root.after`.
        """
        if self.manager.running:
            stats = self.manager.get_stats()
            self.update_stats_display(stats)

            self.root.after(50, self.update_feedback) # Appel récursif après 50 ms
        else:
            solutions = self.manager.get_solutions()
            if solutions:
                self.solution = solutions[0]
                self.solution_steps = self.manager.get_current_solution_steps()
                self.current_step = -1
                self.update_stats_display()
                self.afficher_solution()
            else:
                self.update_info("Aucune solution trouvée.")
                self.afficher_plateau()

            self.enable_controls()

    def display_intermediate_solution(self, current_solution):
        """
        Affiche la solution en cours d'élaboration.
        Utilisée pour fournir un feedback visuel continu pendant la résolution.
        """
        self.reset_board_visuellement()

        for piece_name, data in self.placed_pieces.items():
            color = PIECE_COLORS.get(piece_name, "gray")
            for position in data['positions']:
                i, j = position
                self.cases[i][j].configure(bg=color)

        for step in current_solution:
            piece = step['piece']
            color = PIECE_COLORS.get(piece.nom, "gray")
            for cell in step['cells_covered']:
                i, j = cell
                self.cases[i][j].configure(bg=color)

    def stop_resolution(self):
        """
        Arrête la résolution en cours, que ce soit en mono ou multi-heuristique.
        """
        if hasattr(self, 'manager') and self.manager:
            # Cas mono-heuristique
            self.manager.request_stop()
            self.is_solving = False
            if hasattr(self, 'manager_thread') and self.manager_thread and self.manager_thread.is_alive():
                self.manager_thread.join()
            self.enable_controls()
        elif hasattr(self, 'multi_manager') and self.multi_manager:
            # Cas multi-heuristiques
            self.multi_manager.request_stop_all()
            self.is_solving = False
            # On attend la fin de tous les threads
            for t in self.multi_manager.threads:
                if t.is_alive():
                    t.join()
            self.enable_controls()



    def disable_controls(self):
        """
        Désactive les boutons et autres contrôles pendant la résolution.
        """
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.reset_button.config(state="disabled")
        for piece in self.pieces.values():
            piece.button.config(state="disabled")

    def enable_controls(self):
        """
        Réactive les contrôles une fois la résolution terminée.
        """
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.reset_button.config(state="normal")
        for piece in self.pieces.values():
            piece.button.config(state="normal")

    def display_current_step(self):
        """
        Affiche le plateau à l'étape courante de la solution.
        """
        self.reset_board_visuellement()

        # Réaffiche les pièces initiales
        for piece_name, data in self.placed_pieces.items():
            color = PIECE_COLORS.get(piece_name, "gray")
            for position in data['positions']:
                i, j = position
                self.cases[i][j].configure(bg=color)

        # Applique les étapes jusqu'à current_step inclus
        for step in self.solution_steps[:self.current_step + 1]:
            piece = step['piece']
            color = PIECE_COLORS.get(piece.nom, "gray")
            for cell in step['cells_covered']:
                i, j = cell
                self.cases[i][j].configure(bg=color)

    def afficher_solution(self):
        """
        Affiche la solution finale complète.
        """
        if not self.solution:
            return
        self.reset_board()
        for sol in self.solution:
            piece = sol['piece']
            color = PIECE_COLORS.get(piece.nom, "gray") 
            for cell in sol['cells_covered']:
                i, j = cell
                self.cases[i][j].configure(bg=color)


    def next_step(self):
        """
        Passe à l'étape suivante de la solution (si existe).
        """
        if self.solution_steps and self.current_step < len(self.solution_steps) - 1:
            self.current_step += 1
            self.display_current_step()
        else:
            messagebox.showinfo("Info", "C'est la dernière étape.")

    def previous_step(self):
        """
        Retourne à l'étape précédente de la solution (si possible).
        """
        if self.solution_steps and self.current_step > 0:
            self.current_step -= 1
            self.display_current_step()
        else:
            messagebox.showinfo("Info", "C'est la première étape.")

    def exporter_grille(self):
        """
        Affiche la grille du plateau dans la console (pour debug).
        """
        print("Grille :")
        print("plateau = [")
        for row in self.plateau.plateau:
            print("    ", row.tolist(), ",")
        print("]")

    def update_stats_display(self, stats=None):
        """
        Met à jour l'affichage des informations de l'algorithme (stats).
        Peut être appelée pendant ou après l'exécution.
        Si `stats` est None, elle interroge directement le manager pour obtenir les stats actuelles.

        Paramètres:
        - stats (dict, optional): Dictionnaire contenant les statistiques.
        """
        if stats is None and self.manager:
            stats = self.manager.get_stats()

        if stats:
            elapsed_time = stats.get("time", 0)
            calculs = stats.get("calculs", 0)
            placements_testes = stats.get("placements_testes", 0)
            branches_explored = stats.get("branches_explored", 0)
            branches_pruned = stats.get("branches_pruned", 0)
            max_recursion_depth = stats.get("max_recursion_depth", 0)

            info_text = (
                f"Temps écoulé: {elapsed_time:.2f} s\n"
                f"Calculs effectués: {calculs}\n"
                f"Placements testés: {placements_testes}\n"
                f"Branches explorées: {branches_explored}\n"
                f"Branches coupées: {branches_pruned}\n"
                f"Profondeur maximale de récursion: {max_recursion_depth}\n"
            )
            self.update_info(info_text)


    def reset_board_visuellement(self):
        """
        Réinitialise l'affichage du plateau (cases) en blanc (sans toucher aux données).
        """
        for i in range(self.grid_y):
            for j in range(self.grid_x):
                self.cases[i][j].configure(bg="white")

    def start_resolution_multi(self):
        # Construire fixed_pieces comme avant
        fixed_pieces = {}
        for piece_name, info in self.placed_pieces.items():
            fixed_pieces[piece_name] = {
                'variante_index': info['variante_index'],
                'position': info['position']
            }

        plateau_copy = Plateau()
        plateau_copy.lignes = self.grid_y
        plateau_copy.colonnes = self.grid_x
        plateau_copy.plateau = np.copy(self.plateau.plateau)

        # Liste d'heuristiques à tester en parallèle
        heuristics_list = ["ascender", "descender", "compactness", "holes"]

        self.multi_manager = MultiHeuristicManager(
            plateau_copy,
            self.pieces,
            heuristics_list,
            fixed_pieces
        )

        self.disable_controls()
        self.is_solving = True

        self.multi_manager.run_all()

        # Lancer une mise à jour périodique comme avec update_feedback, mais pour multi
        self.update_feedback_multi()

    def update_feedback_multi(self):
        """
        Met à jour l'interface pendant que la résolution multi-heuristique est en cours.
        Affiche les statistiques de toutes les branches, qu'elles soient en cours ou terminées.
        Ajoute le nom de l'heuristique gagnante une fois que l'une des branches a trouvé une solution.
        """
        # Vérifier si une branche a terminé
        finished, stats, solution, winner_heuristic = self.multi_manager.check_status()

        # Collecter les stats de toutes les branches
        info_text = "Résolution en cours...\nHeuristiques testées:\n"

        # Récupération des stats pour toutes les branches
        for heuristic, manager in self.multi_manager.managers:
            manager_stats = manager.get_stats()
            running = self.multi_manager.results[heuristic]["running"]

            info_text += f"  - {heuristic} : "
            if running:
                info_text += f"{manager_stats['placements_testes']} placements testés, "
                info_text += f"{manager_stats['branches_explored']} branches explorées, "
                info_text += f"{manager_stats['branches_pruned']} branches coupées.\n"
            else:
                # Si terminé, afficher les stats finales
                info_text += f"Terminé. Stats finales : "
                info_text += f"{manager_stats['placements_testes']} placements testés, "
                info_text += f"{manager_stats['branches_explored']} branches explorées, "
                info_text += f"{manager_stats['branches_pruned']} branches coupées.\n"

        # Mettre à jour l'affichage de manière thread-safe
        self.root.after_idle(lambda: self.update_info(info_text))

        if not finished:
            # Continuer la mise à jour périodique tant qu'aucune solution n'est trouvée
            self.root.after(100, self.update_feedback_multi)
        else:
            # Une branche a trouvé une solution
            self.solution = solution
            self.solution_steps = solution
            self.current_step = -1

            # Afficher les statistiques finales et la solution
            self.update_stats_display(stats)
            if winner_heuristic:
                self.update_info(f"Solution trouvée par l'heuristique: {winner_heuristic}")
            else:
                self.update_info("Solution trouvée (aucune heuristique identifiée).")

            # Afficher la solution et réactiver les contrôles
            self.afficher_solution()
            self.enable_controls()


    def stop_resolution_multi(self):
        """
        Arrête toutes les branches de résolution en cours.
        """
        if self.multi_solver:
            self.multi_solver.stop_all()
            self.enable_controls()

