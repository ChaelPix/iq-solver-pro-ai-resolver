import tkinter as tk
from tkinter import messagebox
from piece import Piece
from plateau import Plateau
from tkinter import messagebox, filedialog 
import json
import numpy as np
import time
import itertools
from multiprocessing import Process, Manager

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
        self.reset_button = tk.Button(self.controls_frame, text="Reset Board", command=self.reset_board)
        self.reset_button.grid(row=0, column=2, padx=5)
        self.save_button = tk.Button(self.controls_frame, text="Save Board", command=self.sauvegarder_plateau)
        self.save_button.grid(row=0, column=3, padx=5)
        self.load_button = tk.Button(self.controls_frame, text="Load Board", command=self.charger_plateau)
        self.load_button.grid(row=0, column=4, padx=5)

        self.info_frame = tk.Frame(self.root)
        self.info_frame.grid(row=3, column=0, padx=10, pady=10)
        self.info_label = tk.Label(self.info_frame, text="Informations sur l'algorithme", font=("Arial", 14))
        self.info_label.pack()
        self.info_text = tk.Text(self.info_frame, width=80, height=5, state="disabled")
        self.info_text.pack()

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
        """Démarre l'algorithme pour résoudre le puzzle et affiche la solution."""
        self.solution = [] 

        fixed_pieces = {}
        for piece_name, info in self.placed_pieces.items():
            fixed_pieces[piece_name] = {
                'variante_index': info['variante_index'],
                'position': info['position']
            }

        plateau_copy = Plateau()
        plateau_copy.plateau = np.copy(self.plateau.plateau)

        algo = AlgorithmX(plateau_copy, self.pieces, fixed_pieces, update_callback=self.update_stats)
        solutions = algo.solve()

        if solutions:
            self.solution = solutions[0] 
            algo.print_solution()
            self.afficher_solution()
        else:
            print("Aucune solution trouvée.")

    def afficher_solution(self):
        """Affiche la solution trouvée sur le plateau graphique."""
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
        """Met à jour les informations dans l'interface et affiche les placements en cours."""
        elapsed_time = stats["time"]
        calculs = stats["calculs"]
        placements_testes = stats["placements_testes"]
        solution = stats["solution"]

        info_text = (
            f"Temps écoulé: {elapsed_time:.2f} s\n"
            f"Calculs effectués: {calculs}\n"
            f"Placements testés: {placements_testes}\n"
            f"Nombre de solutions trouvées: {len(self.solution)}\n"
        )
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", info_text)
        self.info_text.config(state="disabled")

        self.reset_board()
        for sol in solution:
            piece = sol['piece']
            color = PIECE_COLORS.get(piece.nom, "gray")
            for cell in sol['cells_covered']:
                i, j = cell
                self.cases[i][j].configure(bg=color)

        self.root.update()


    def reset_board_visuellement(self):
        """Efface le plateau et réinitialise toutes les cases visuellement."""
        for i in range(5):
            for j in range(11):
                self.cases[i][j].configure(bg="white")

class AlgorithmX:
    def __init__(self, plateau, pieces, fixed_pieces=None, update_callback=None):
        self.plateau = plateau
        self.pieces = pieces
        self.solutions = []
        self.fixed_pieces = fixed_pieces if fixed_pieces else {}
        self.update_callback = update_callback 

        self.calculs = 0
        self.placements_testes = 0
        self.start_time = time.time()

        self.zone_cache = {}
        self.invalid_placements = {}

    def solve(self):
        """Lance l'algorithme pour trouver une solution unique et l'affiche sur le plateau."""
        matrix, header = self.create_constraint_matrix()
        solution = []
        self.algorithm_x(matrix, header, solution)
        return self.solutions

    def create_constraint_matrix(self):
        """Crée une matrice de contraintes en tenant compte des pièces et variantes, optimisée par l'ordre des priorités."""
        num_cells = self.plateau.lignes * self.plateau.colonnes
        num_pieces = len(self.pieces)
        total_columns = num_cells + num_pieces

        header = ['C{}'.format(i) for i in range(num_cells)] + [piece.nom for piece in self.pieces.values()]
        matrix = []
        used_pieces = set(self.fixed_pieces.keys())
        pieces_non_fixees = [piece for piece in self.pieces.values() if piece.nom not in used_pieces]
        pieces_non_fixees.sort(key=lambda p: len(p.variantes))

        for piece in pieces_non_fixees:
            for variante_index, variante in enumerate(piece.variantes):
                for i in range(self.plateau.lignes):
                    for j in range(self.plateau.colonnes):
                        position = (i, j)
                        if self.plateau.peut_placer(variante, position):
                            row = [0] * total_columns
                            cells_covered = []
                            for vi in range(variante.shape[0]):
                                for vj in range(variante.shape[1]):
                                    if variante[vi, vj] == 1:
                                        cell_index = (i + vi) * self.plateau.colonnes + (j + vj)
                                        row[cell_index] = 1
                                        cells_covered.append((i + vi, j + vj))
                            piece_index = num_cells + list(self.pieces.keys()).index(piece.nom)
                            row[piece_index] = 1
                            matrix.append({
                                'row': row,
                                'piece': piece,
                                'variante_index': variante_index,
                                'position': position,
                                'cells_covered': cells_covered
                            })

        for piece_name, info in self.fixed_pieces.items():
            piece = self.pieces[piece_name]
            variante_index = info['variante_index']
            position = info['position']
            variante = piece.variantes[variante_index]

            row = [0] * total_columns
            cells_covered = []
            for vi in range(variante.shape[0]):
                for vj in range(variante.shape[1]):
                    if variante[vi, vj] == 1:
                        cell_index = (position[0] + vi) * self.plateau.colonnes + (position[1] + vj)
                        row[cell_index] = 1
                        cells_covered.append((position[0] + vi, position[1] + vj))
            piece_index = num_cells + list(self.pieces.keys()).index(piece_name)
            row[piece_index] = 1
            matrix.insert(0, {
                'row': row,
                'piece': piece,
                'variante_index': variante_index,
                'position': position,
                'cells_covered': cells_covered,
                'fixed': True
            })

        return matrix, header

    def algorithm_x(self, matrix, header, solution):
        """Exécute une branche unique pour afficher son avancement et arrête dès qu'une solution est trouvée."""
        if not any(row['row'] for row in matrix):
            if self.validate_solution(solution):
                self.solutions.append(solution.copy())
                return True 
            return False

        counts = [0] * len(header)
        for row in matrix:
            for idx, val in enumerate(row['row']):
                if val == 1:
                    counts[idx] += 1

        counts = [count if any(row['row'][idx] == 1 for row in matrix) else float('inf') for idx, count in enumerate(counts)]
        min_count = min(counts)
        if min_count == float('inf'):
            return False

        column = counts.index(min_count)
        rows_to_cover = [row for row in matrix if row['row'][column] == 1]

        rows_to_cover.sort(key=lambda r: -np.count_nonzero(r['piece'].forme_base))

        for row in rows_to_cover:
            solution.append(row)
            self.placements_testes += 1

            self.update_interface(solution)

            columns_to_remove = [idx for idx, val in enumerate(row['row']) if val == 1]
            new_matrix = []
            for r in matrix:
                if r == row:
                    continue
                if all(r['row'][idx] == 0 for idx in columns_to_remove):
                    new_matrix.append(r)

            if not self.has_unfillable_voids(solution):
                if self.algorithm_x(new_matrix, header, solution):
                    return True

            solution.pop()
            self.calculs += 1
        return False

    def algorithm_x_parallel(self, matrix, header, solution):
        """Lance l'algorithme X avec multiprocessing, chaque branche principale étant traitée dans un processus séparé."""
        if not any(row['row'] for row in matrix):
            if self.validate_solution(solution):
                self.solutions.append(solution.copy())
            return

        counts = [0] * len(header)
        for row in matrix:
            for idx, val in enumerate(row['row']):
                if val == 1:
                    counts[idx] += 1

        counts = [count if any(row['row'][idx] == 1 for row in matrix) else float('inf') for idx, count in enumerate(counts)]
        min_count = min(counts)
        if min_count == float('inf'):
            return

        column = counts.index(min_count)
        rows_to_cover = [row for row in matrix if row['row'][column] == 1]

        rows_to_cover.sort(key=lambda r: -np.count_nonzero(r['piece'].forme_base))

        processes = []
        for row in rows_to_cover:
            p = Process(target=self.process_branch, args=(row, matrix, header, solution))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    def process_branch(self, row, matrix, header, solution):
        """Traite une branche spécifique de manière indépendante pour l'exécution en parallèle."""
        solution.append(row)
        piece_name = row['piece'].nom
        variante_index = row['variante_index']
        position = row['position']
        key = (piece_name, variante_index, position)

        if key in self.invalid_placements:
            solution.pop()
            return

        columns_to_remove = [idx for idx, val in enumerate(row['row']) if val == 1]
        new_matrix = []
        for r in matrix:
            if r == row:
                continue
            if all(r['row'][idx] == 0 for idx in columns_to_remove):
                new_matrix.append(r)

        if not self.has_unfillable_voids(solution):
            self.algorithm_x_parallel(new_matrix, header, solution)
        else:
            self.invalid_placements[key] = True

        solution.pop()

    def has_unfillable_voids(self, solution):
        """Vérifie si le plateau contient des zones vides impossibles à remplir avec les pièces restantes."""
        plateau_temp = np.copy(self.plateau.plateau)
        for sol in solution:
            for cell in sol['cells_covered']:
                i, j = cell
                plateau_temp[i, j] = 1  # Marque les cellules couvertes comme occupées

        empty_zones = self.get_empty_zones(plateau_temp)
        remaining_pieces = set(self.pieces.keys()) - set(sol['piece'].nom for sol in solution)
        remaining_sizes = [np.count_nonzero(self.pieces[piece_name].forme_base) for piece_name in remaining_pieces]

        for zone in empty_zones:
            zone_size = len(zone)
            if zone_size in self.zone_cache:
                if not self.zone_cache[zone_size]:
                    return True
                else:
                    continue

            possible = False
            for i in range(1, len(remaining_sizes)+1):
                for combo in itertools.combinations(remaining_sizes, i):
                    if sum(combo) == zone_size:
                        possible = True
                        break
                if possible:
                    break
            self.zone_cache[zone_size] = possible
            if not possible:
                return True
        return False

    def get_empty_zones(self, plateau_temp):
        """Retourne une liste des zones vides contiguës sur le plateau."""
        visited = set()
        empty_zones = []
        for i in range(self.plateau.lignes):
            for j in range(self.plateau.colonnes):
                if plateau_temp[i, j] == 0 and (i, j) not in visited:
                    zone = self.explore_zone(plateau_temp, i, j, visited)
                    empty_zones.append(zone)
        return empty_zones

    def explore_zone(self, plateau_temp, i, j, visited):
        """Explore une zone vide contiguë et retourne la liste de ses cellules."""
        queue = [(i, j)]
        visited.add((i, j))
        zone = [(i, j)]

        while queue:
            ci, cj = queue.pop(0)
            for ni, nj in [(ci+1, cj), (ci-1, cj), (ci, cj+1), (ci, cj-1)]:
                if (0 <= ni < self.plateau.lignes and 0 <= nj < self.plateau.colonnes
                        and plateau_temp[ni, nj] == 0 and (ni, nj) not in visited):
                    visited.add((ni, nj))
                    queue.append((ni, nj))
                    zone.append((ni, nj))
        return zone

    def update_interface(self, solution):
        """Appelle la fonction de mise à jour de l'interface pour afficher une seule branche en temps réel."""
        if self.update_callback:
            elapsed_time = time.time() - self.start_time
            stats = {
                "time": elapsed_time,
                "calculs": self.calculs,
                "placements_testes": self.placements_testes,
                "solution": solution
            }
            self.update_callback(stats)

    def validate_solution(self, solution):
        pieces_used = set()
        cells_covered = set()

        for sol in solution:
            piece_name = sol['piece'].nom
            if piece_name in pieces_used:
                return False
            pieces_used.add(piece_name)

            for cell in sol['cells_covered']:
                if cell in cells_covered:
                    return False
                cells_covered.add(cell)

        all_pieces_used = len(pieces_used) == len(self.pieces)
        full_board_covered = len(cells_covered) == (self.plateau.lignes * self.plateau.colonnes)
        return all_pieces_used and full_board_covered

    def print_solution(self):
        if not self.solutions:
            print("Aucune solution trouvée.")
            return
        print("Solution trouvée :")
        for sol in self.solutions[0]:
            piece = sol['piece']
            position = sol['position']
            print(f"Placer la pièce {piece.nom} en position {position} avec la variante {sol['variante_index']}")



if __name__ == "__main__":
    root = tk.Tk()
    interface = IQPuzzlerInterface(root)
    root.mainloop()
