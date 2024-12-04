import tkinter as tk
from tkinter import messagebox, filedialog
import json
from piece import Piece
from plateau import Plateau
import numpy as np
from algo_x_knuth import AlgorithmX
import csv
import threading
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
        self.solution = None
        self.plateau = Plateau()

        self.team_label = tk.Label(self.root, text="IA41 Projet - Antoine & Traïan", font=("Arial", 10))
        self.team_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)

        self.plateau_frame = tk.Frame(self.root)
        self.plateau_frame.grid(row=0, column=0, padx=10, pady=10)
        self.cases = [[None for _ in range(11)] for _ in range(5)]
        self.init_plateau()

        self.pieces_frame = tk.Frame(self.root)
        self.pieces_frame.grid(row=1, column=0, padx=10, pady=10)
        self.pieces = {}
        self.load_pieces()

        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.rotate_button = tk.Button(self.controls_frame, text="Rotate", command=self.rotate_piece)
        self.rotate_button.grid(row=0, column=0, padx=5)
        self.start_button = tk.Button(self.controls_frame, text="Start", command=self.start_resolution)
        self.start_button.grid(row=0, column=1, padx=5)
        self.start_button = tk.Button(self.controls_frame, text="Stop", command=self.stop)
        self.start_button.grid(row=0, column=2, padx=5)
        self.reset_button = tk.Button(self.controls_frame, text="Reset Board", command=self.reset_board)
        self.reset_button.grid(row=0, column=3, padx=5)
        self.save_button = tk.Button(self.controls_frame, text="Save Board", command=self.sauvegarder_plateau)
        self.save_button.grid(row=0, column=4, padx=5)
        self.load_button = tk.Button(self.controls_frame, text="Load Board", command=self.charger_plateau)
        self.load_button.grid(row=0, column=5, padx=5)

        self.current_step = 0
        self.next_button = tk.Button(self.controls_frame, text="Next Step", command=self.next_step)
        self.next_button.grid(row=0, column=7, padx=5)
        self.prev_button = tk.Button(self.controls_frame, text="Previous Step", command=self.prev_step)
        self.prev_button.grid(row=0, column=6, padx=5)

        self.info_frame = tk.Frame(self.root)
        self.info_frame.grid(row=3, column=0, padx=10, pady=10)
        self.info_label = tk.Label(self.info_frame, text="Informations sur l'algorithme", font=("Arial", 14))
        self.info_label.pack()
        self.info_text = tk.Text(self.info_frame, width=80, height=5, state="disabled")
        self.info_text.pack()

        self.export_button = tk.Button(self.controls_frame, text="Export Solution", command=self.export_solutions)
        self.export_button.grid(row=0, column=8, padx=5)

        self.placed_pieces = {}
        self.algo = AlgorithmX(Plateau(), self.pieces, {}, update_callback=self.update_stats)
        self.isRunning = False

    def stop(self):
        self.isRunning = False
        self.algo.stop()
        if hasattr(self.algo, 'threads'):
            for thread in self.algo.threads:
                thread.join()

    def init_plateau(self):
        for i in range(5):
            for j in range(11):
                case = tk.Label(self.plateau_frame, width=4, height=2, borderwidth=1, relief="solid", bg="white")
                case.grid(row=i, column=j)
                case.bind("<Button-1>", lambda e, x=i, y=j: self.handle_grid_click(x, y))
                self.cases[i][j] = case

    def afficher_plateau(self):
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

    def afficher_solution_finale(self):
        """Affiche la solution complète, c'est-à-dire la dernière étape."""
        if not self.algo.solution_steps:
            return
        self.current_step = len(self.algo.solution_steps) - 1
        self.afficher_etape(self.current_step)

    def afficher_etape(self, step_index):
        """Affiche une étape spécifique de la solution."""
        self.reset_board_visuellement()
        step = self.algo.solution_steps[step_index]
        
        for sol in step:
            piece = sol['piece']
            color = PIECE_COLORS.get(piece.nom, "gray")
            for cell in sol['cells_covered']:
                i, j = cell
                self.cases[i][j].configure(bg=color)
        self.root.update()

    def next_step(self):
        """Affiche l'étape suivante si disponible."""
        if self.current_step < len(self.algo.solution_steps) - 1:
            self.current_step += 1
            self.afficher_etape(self.current_step)

    def prev_step(self):
        """Affiche l'étape précédente si disponible."""
        if self.current_step >= self.algo.nbr_pieces_init:
            self.current_step -= 1
            self.afficher_etape(self.current_step)

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
        self.isRunning = True  # Indiquer que l'algorithme est en cours d'exécution
        self.algo = AlgorithmX(plateau_copy, self.pieces, fixed_pieces, update_callback=self.update_stats)

        # Créer un thread pour exécuter l'algorithme
        def run_algorithm():
            self.algo.solve()
            self.isRunning = False  # Indiquer que l'algorithme a terminé

        threading.Thread(target=run_algorithm).start()

        # Démarrer les mises à jour périodiques de l'interface
        self.update_interface_periodically()


    def update_interface_periodically(self):
        if(not self.isRunning):
            return None
        # Mettre à jour l'interface ici si nécessaire
        self.update_stats_in_interface()
        # Re-planifier cette méthode après 100 ms
        self.root.after(50, self.update_interface_periodically)

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

    def exporter_grille(self):
        print("Grille :")
        print("plateau = [")
        for row in self.plateau.plateau:
            print("    ", row.tolist(), ",")
        print("]")

    def update_stats(self, stats):
        self.latest_stats = stats

    def update_stats_in_interface(self):
        if hasattr(self, 'latest_stats'):
            stats = self.latest_stats
            elapsed_time = stats["time"]
            calculs = stats["calculs"]
            placements_testes = stats["placements_testes"]
            solution = stats["solution"]

            info_text = (
                f"Temps écoulé: {elapsed_time:.2f} s\n"
                f"Calculs effectués: {calculs}\n"
                f"Placements testés: {placements_testes}\n"
                f"Nombre de solutions trouvées: {len(self.algo.solutions)}\n"
            )
            self.info_text.config(state="normal")
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert("1.0", info_text)
            self.info_text.config(state="disabled")

            # Mettre à jour le plateau visuellement si nécessaire
            if solution:
                self.reset_board_visuellement()
                for sol in solution:
                    piece = sol['piece']
                    color = PIECE_COLORS.get(piece.nom, "gray")
                    for cell in sol['cells_covered']:
                        i, j = cell
                        self.cases[i][j].configure(bg=color)

    def reset_board_visuellement(self):
        """Efface le plateau et réinitialise toutes les cases visuellement."""
        for i in range(5):
            for j in range(11):
                self.cases[i][j].configure(bg="white")
    

    def export_solutions(self):
        if not self.algo.solution_steps:
            messagebox.showinfo("Information", "Aucune solution à exporter.")
            return

        fichier = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Fichiers CSV", "*.csv")])
        if not fichier:
            return

        fixed_pieces_names = set(self.placed_pieces.keys())

        with open(fichier, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header = ['Posx', 'Posy']
            header += ['Piece1pos{}'.format(i) for i in range(16)]
            header += ['InitPos{}'.format(i) for i in range(55)]
            header += ['FinalPos{}'.format(i) for i in range(55)]
            writer.writerow(header)

            for step_index in range(1, len(self.algo.solution_steps)):
                step = self.algo.solution_steps[step_index]
                previous_step = self.algo.solution_steps[step_index - 1]

                current_pieces = set([sol['piece'].nom for sol in step])
                previous_pieces = set([sol['piece'].nom for sol in previous_step])

                current_pieces -= fixed_pieces_names
                previous_pieces -= fixed_pieces_names

                new_pieces = current_pieces - previous_pieces

                if not new_pieces:
                    continue 

                new_piece_name = new_pieces.pop()
                new_piece_sol = next(sol for sol in step if sol['piece'].nom == new_piece_name)

                posx, posy = new_piece_sol['position']

                piece_matrix = np.zeros((4, 4), dtype=int)
                variante = new_piece_sol['piece'].variantes[new_piece_sol['variante_index']]
                shape = variante.shape
                for i in range(shape[0]):
                    for j in range(shape[1]):
                        if variante[i, j]:
                            piece_matrix[i, j] = 1
                piece_matrix_flat = piece_matrix.flatten()

                init_board = np.zeros((5, 11), dtype=int)
                for sol in previous_step:
                    if sol['piece'].nom in fixed_pieces_names:
                        continue 
                    for cell in sol['cells_covered']:
                        i, j = cell
                        init_board[i, j] = 1
                init_board_flat = init_board.flatten()

                final_board = np.zeros((5, 11), dtype=int)
                for sol in step:
                    if sol['piece'].nom in fixed_pieces_names:
                        continue
                    for cell in sol['cells_covered']:
                        i, j = cell
                        final_board[i, j] = 1
                final_board_flat = final_board.flatten()

                row = [posx, posy]
                row += piece_matrix_flat.tolist()
                row += init_board_flat.tolist()
                row += final_board_flat.tolist()

                writer.writerow(row)

        messagebox.showinfo("Exportation", "solutions exported")

