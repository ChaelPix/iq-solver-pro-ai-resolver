import itertools
import numpy as np
import time
from multiprocessing import Process, Manager

class InterfaceBridge:
    """
    Classe mère pour la gestion de l'interface et le suivi des statistiques.
    """

    def __init__(self, update_callback=None):
        """
        Initialise la gestion de l'interface.

        Paramètres:
        - update_callback (function): Fonction de rappel pour les mises à jour de l'interface.
        """
        self.update_callback = update_callback
        self.calculs = 0  # Nombre total de calculs effectués.
        self.placements_testes = 0  # Nombre de placements testés.
        self.start_time = time.time()  # Temps de démarrage de l'algorithme.
        self.stop_requested = False  # Drapeau pour arrêter l'algorithme.
        self.solution_steps = []  # Liste pour stocker les étapes de la solution.

    def update_interface(self, solution):
        """
        Met à jour l'interface avec les statistiques actuelles.

        Paramètres:
        - solution (list): Liste actuelle des placements de pièces.
        """
        if self.update_callback:
            elapsed_time = time.time() - self.start_time
            stats = {
                "time": elapsed_time,
                "calculs": self.calculs,
                "placements_testes": self.placements_testes,
                "solution": solution.copy()
            }
            self.update_callback(stats)

    def request_stop(self):
        """
        Demande l'arrêt de l'algorithme.
        """
        self.stop_requested = True

    def get_solution_steps(self):
        """
        Retourne les étapes de la solution finale.

        Retourne:
        - solution_steps (list): Liste des placements de pièces dans l'ordre.
        """
        return self.solution_steps.copy()

class AlgorithmX(InterfaceBridge):
    """
    Implémente l'algorithme X de Knuth pour résoudre un problème de couverture exacte.
    """

    def __init__(self, plateau, pieces, fixed_pieces=None, update_callback=None):
        """
        Initialise l'algorithme avec le plateau et les pièces.

        Paramètres:
        - plateau (Plateau): Objet représentant le plateau de jeu.
        - pieces (dict): Dictionnaire des pièces disponibles, indexées par leur nom.
        - fixed_pieces (dict): (Optionnel) Dictionnaire des pièces déjà placées avec leur position et variante.
        - update_callback (function): (Optionnel) Fonction de rappel pour les mises à jour de l'interface.
        """
        super().__init__(update_callback)
        self.plateau = plateau  # Plateau de jeu.
        self.pieces = pieces  # Dictionnaire des pièces disponibles.
        self.fixed_pieces = fixed_pieces if fixed_pieces else {}  # Pièces fixées.
        self.solutions = []  # Liste des solutions trouvées.
        self.zone_cache = {}  # Cache pour les zones vides déjà évaluées.
        self.invalid_placements = {}  # Cache pour les placements invalides.

        # Heuristique : poids des pièces pour la priorisation lors du placement.
        self.piece_weights = self.calculate_piece_weights()

    def calculate_piece_weights(self):
        """
        Calcule les poids des pièces pour l'heuristique de priorisation,
        en donnant plus d'importance aux pièces occupant moins d'espace.

        Retourne:
        - piece_weights (dict): Dictionnaire des poids pour chaque pièce.
        """
        weights = {}
        for piece in self.pieces.values():
            # Plus la pièce occupe peu de cellules, plus son poids est élevé.
            occupied_cells = np.count_nonzero(piece.forme_base)
            weight = 1 / occupied_cells if occupied_cells > 0 else float('inf')
            weights[piece.nom] = weight
        return weights

    def solve(self):
        """
        Lance la résolution du problème en utilisant l'algorithme X.

        Retourne:
        - solutions (list): Liste des solutions trouvées.
        """
        matrix, header = self.create_constraint_matrix()
        solution = []
        self.algorithm_x(matrix, header, solution)
        return self.solutions

    def create_constraint_matrix(self):
        """
        Crée la matrice de contraintes pour l'algorithme X.

        Retourne:
        - matrix (list): Liste des possibilités de placement des pièces.
        - header (list): En-tête de la matrice représentant les colonnes.
        """
        num_cells = self.plateau.lignes * self.plateau.colonnes  # Nombre total de cellules du plateau.
        num_pieces = len(self.pieces)  # Nombre total de pièces.
        total_columns = num_cells + num_pieces  # Nombre total de colonnes dans la matrice.

        # Création de l'en-tête : colonnes pour chaque cellule du plateau et pour chaque pièce.
        header = ['C{}'.format(i) for i in range(num_cells)] + [piece.nom for piece in self.pieces.values()]

        matrix = []  # Liste pour stocker les lignes de la matrice de contraintes.

        used_pieces = set(self.fixed_pieces.keys())  # Pièces déjà utilisées (fixées).

        # Liste des pièces non fixées.
        pieces_non_fixees = [piece for piece in self.pieces.values() if piece.nom not in used_pieces]
        # Tri des pièces selon l'heuristique (ici, par poids décroissant).
        pieces_non_fixees.sort(key=lambda p: -self.piece_weights[p.nom])

        # Génération des lignes pour les pièces non fixées.
        for piece in pieces_non_fixees:
            self.add_piece_to_matrix(piece, matrix, num_cells)

        # Ajout des pièces fixées au début de la matrice.
        for piece_name, info in self.fixed_pieces.items():
            piece = self.pieces[piece_name]
            self.add_fixed_piece_to_matrix(piece, info, matrix, num_cells)

        return matrix, header

    def add_piece_to_matrix(self, piece, matrix, num_cells):
        """
        Ajoute les différentes possibilités de placement d'une pièce non fixée à la matrice de contraintes.

        Paramètres:
        - piece (Piece): La pièce à ajouter.
        - matrix (list): La matrice de contraintes à mettre à jour.
        - num_cells (int): Nombre total de cellules du plateau.
        """
        for variante_index, variante in enumerate(piece.variantes):
            for i in range(self.plateau.lignes):
                for j in range(self.plateau.colonnes):
                    position = (i, j)  # Position actuelle sur le plateau.
                    if self.plateau.peut_placer(variante, position):
                        row, cells_covered = self.create_row_for_placement(piece, variante, position, num_cells)
                        piece_index = num_cells + list(self.pieces.keys()).index(piece.nom)
                        row[piece_index] = 1
                        matrix.append({
                            'row': row,
                            'piece': piece,
                            'variante_index': variante_index,
                            'position': position,
                            'cells_covered': cells_covered
                        })

    def add_fixed_piece_to_matrix(self, piece, info, matrix, num_cells):
        """
        Ajoute une pièce fixée à la matrice de contraintes.

        Paramètres:
        - piece (Piece): La pièce fixée.
        - info (dict): Informations sur la variante et la position de la pièce.
        - matrix (list): La matrice de contraintes à mettre à jour.
        - num_cells (int): Nombre total de cellules du plateau.
        """
        variante_index = info['variante_index']
        position = info['position']
        variante = piece.variantes[variante_index]

        row, cells_covered = self.create_row_for_placement(piece, variante, position, num_cells)
        piece_index = num_cells + list(self.pieces.keys()).index(piece.nom)
        row[piece_index] = 1
        matrix.insert(0, {
            'row': row,
            'piece': piece,
            'variante_index': variante_index,
            'position': position,
            'cells_covered': cells_covered,
            'fixed': True
        })

    def create_row_for_placement(self, piece, variante, position, num_cells):
        """
        Crée une ligne de la matrice de contraintes pour un placement donné.

        Paramètres:
        - piece (Piece): La pièce concernée.
        - variante (np.ndarray): Variante de la pièce à placer.
        - position (tuple): Position (i, j) sur le plateau.
        - num_cells (int): Nombre total de cellules du plateau.

        Retourne:
        - row (list): Ligne de la matrice de contraintes représentant ce placement.
        - cells_covered (list): Liste des cellules couvertes par ce placement.
        """
        total_columns = num_cells + len(self.pieces)
        row = [0] * total_columns  # Initialisation de la ligne de contraintes.
        cells_covered = []  # Cellules couvertes par ce placement.

        for vi in range(variante.shape[0]):
            for vj in range(variante.shape[1]):
                if variante[vi, vj] == 1:
                    cell_row = position[0] + vi
                    cell_col = position[1] + vj
                    cell_index = cell_row * self.plateau.colonnes + cell_col
                    row[cell_index] = 1
                    cells_covered.append((cell_row, cell_col))

        return row, cells_covered

    def algorithm_x(self, matrix, header, solution):
        """
        Implémente l'algorithme X de Knuth pour résoudre le problème de couverture exacte.

        Paramètres:
        - matrix (list): Matrice de contraintes actuelle.
        - header (list): En-tête de la matrice.
        - solution (list): Liste des placements sélectionnés jusqu'à présent.

        Retourne:
        - bool: True si une solution est trouvée, False sinon.
        """
        if self.stop_requested:
            return False  # Arrêter l'algorithme si demandé.

        if not matrix:
            if self.validate_solution(solution):
                self.solutions.append(solution.copy())
                self.solution_steps = solution.copy()  # Stocker les étapes de la solution.
                return True  # Trouvé une solution complète.
            return False  # Pas de solution valide.

        column = self.select_min_column(matrix, header)
        if column is None:
            return False

        rows_to_cover = [row for row in matrix if row['row'][column] == 1]

        # Heuristique : trier les lignes (placements) par priorité.
        rows_to_cover = self.prioritize_rows(rows_to_cover)

        for row in rows_to_cover:
            if self.stop_requested:
                return False  # Arrêter l'algorithme si demandé.

            solution.append(row)
            self.placements_testes += 1

            self.update_interface(solution)

            columns_to_remove = [idx for idx, val in enumerate(row['row']) if val == 1]
            new_matrix = self.cover_columns(matrix, columns_to_remove, row)

            if not self.has_unfillable_voids(solution):
                if self.algorithm_x(new_matrix, header, solution):
                    return True  # Solution trouvée.

            solution.pop()
            self.calculs += 1
        return False  # Pas de solution sur ce chemin.


    def select_min_column(self, matrix, header):
        """
        Sélectionne la colonne avec le moins d'options possibles (heuristique MRV).

        Paramètres:
        - matrix (list): Matrice de contraintes actuelle.
        - header (list): En-tête de la matrice.

        Retourne:
        - column (int): Index de la colonne sélectionnée, ou None si aucune colonne.
        """
        counts = [0] * len(header)
        for row in matrix:
            for idx, val in enumerate(row['row']):
                if val == 1:
                    counts[idx] += 1

        # Ignorer les colonnes sans options (mettre à l'infini pour ne pas les sélectionner).
        counts = [count if count > 0 else float('inf') for count in counts]
        min_count = min(counts)
        if min_count == float('inf'):
            return None  # Plus de colonnes à couvrir.

        column = counts.index(min_count)
        return column

    def prioritize_rows(self, rows):
        """
        Priorise les lignes (placements) selon une heuristique.

        Paramètres:
        - rows (list): Liste des lignes à prioriser.

        Retourne:
        - rows (list): Liste des lignes triées selon la priorité.
        """
        # Heuristique : trier par poids de la pièce (taille), plus les pièces sont grandes, plus elles sont placées en premier.
        rows.sort(key=lambda r: -self.piece_weights[r['piece'].nom])
        return rows

    def cover_columns(self, matrix, columns_to_remove, selected_row):
        """
        Met à jour la matrice en supprimant les colonnes et lignes couvertes par le placement sélectionné.

        Paramètres:
        - matrix (list): Matrice de contraintes actuelle.
        - columns_to_remove (list): Index des colonnes à supprimer.
        - selected_row (dict): Placement sélectionné.

        Retourne:
        - new_matrix (list): Nouvelle matrice de contraintes mise à jour.
        """
        new_matrix = []
        for r in matrix:
            if r == selected_row:
                continue
            # Vérifie si la ligne n'est pas affectée par les colonnes supprimées.
            if all(r['row'][idx] == 0 for idx in columns_to_remove):
                new_matrix.append(r)
        return new_matrix

    def has_unfillable_voids(self, solution):
        """
        Vérifie s'il existe des zones vides impossibles à remplir avec les pièces restantes.

        Paramètres:
        - solution (list): Liste des placements sélectionnés jusqu'à présent.

        Retourne:
        - bool: True si des zones non remplies ne peuvent être comblées, False sinon.
        """
        plateau_temp = self.apply_solution_to_plateau(solution)
        empty_zones = self.get_empty_zones(plateau_temp)
        remaining_pieces = set(self.pieces.keys()) - set(sol['piece'].nom for sol in solution)
        remaining_sizes = [np.count_nonzero(self.pieces[piece_name].forme_base) for piece_name in remaining_pieces]

        for zone in empty_zones:
            zone_size = len(zone)
            if zone_size in self.zone_cache:
                if not self.zone_cache[zone_size]:
                    return True  # Zone déjà connue comme non comblable.
                else:
                    continue  # Zone comblable connue.

            possible = self.is_zone_fillable(zone_size, remaining_sizes)
            self.zone_cache[zone_size] = possible
            if not possible:
                return True  # Zone non comblable détectée.
        return False  # Pas de zones non comblables.

    def apply_solution_to_plateau(self, solution):
        """
        Applique les placements de la solution actuelle au plateau temporaire.

        Paramètres:
        - solution (list): Liste des placements sélectionnés jusqu'à présent.

        Retourne:
        - plateau_temp (np.ndarray): Plateau temporaire avec les placements appliqués.
        """
        plateau_temp = np.copy(self.plateau.plateau)
        for sol in solution:
            for cell in sol['cells_covered']:
                i, j = cell
                plateau_temp[i, j] = 1  # Marquer la cellule comme occupée.
        return plateau_temp

    def get_empty_zones(self, plateau_temp):
        """
        Trouve toutes les zones vides sur le plateau temporaire.

        Paramètres:
        - plateau_temp (np.ndarray): Plateau temporaire avec les placements actuels.

        Retourne:
        - empty_zones (list): Liste des zones vides, chaque zone étant une liste de coordonnées.
        """
        visited = set()
        empty_zones = []
        for i in range(self.plateau.lignes):
            for j in range(self.plateau.colonnes):
                if plateau_temp[i, j] == 0 and (i, j) not in visited:
                    zone = self.explore_zone(plateau_temp, i, j, visited)
                    empty_zones.append(zone)
        return empty_zones

    def explore_zone(self, plateau_temp, i, j, visited):
        """
        Explore une zone vide à partir d'une position donnée.

        Paramètres:
        - plateau_temp (np.ndarray): Plateau temporaire.
        - i (int): Coordonnée i (ligne) de départ.
        - j (int): Coordonnée j (colonne) de départ.
        - visited (set): Ensemble des positions déjà visitées.

        Retourne:
        - zone (list): Liste des positions constituant la zone vide.
        """
        queue = [(i, j)]
        visited.add((i, j))
        zone = [(i, j)]

        while queue:
            ci, cj = queue.pop(0)
            neighbors = self.get_neighbors(ci, cj)
            for ni, nj in neighbors:
                if (0 <= ni < self.plateau.lignes and 0 <= nj < self.plateau.colonnes
                        and plateau_temp[ni, nj] == 0 and (ni, nj) not in visited):
                    visited.add((ni, nj))
                    queue.append((ni, nj))
                    zone.append((ni, nj))
        return zone

    def get_neighbors(self, i, j):
        """
        Obtient les positions voisines d'une cellule donnée.

        Paramètres:
        - i (int): Coordonnée i (ligne) de la cellule.
        - j (int): Coordonnée j (colonne) de la cellule.

        Retourne:
        - neighbors (list): Liste des positions voisines (i, j).
        """
        return [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]

    def is_zone_fillable(self, zone_size, remaining_sizes):
        """
        Vérifie si une zone de taille donnée peut être remplie avec les pièces restantes.

        Paramètres:
        - zone_size (int): Taille de la zone vide.
        - remaining_sizes (list): Tailles des pièces restantes.

        Retourne:
        - possible (bool): True si la zone peut être remplie, False sinon.
        """
        # Vérifie si la somme de combinaisons de tailles de pièces peut atteindre la taille de la zone.
        possible = self.can_fill_zone(zone_size, remaining_sizes)
        return possible

    def can_fill_zone(self, zone_size, piece_sizes):
        """
        Vérifie si une combinaison de pièces peut remplir la zone.

        Paramètres:
        - zone_size (int): Taille de la zone à remplir.
        - piece_sizes (list): Tailles des pièces disponibles.

        Retourne:
        - bool: True si la zone peut être remplie, False sinon.
        """
        # Utilise un algorithme de programmation dynamique pour déterminer si une combinaison est possible.
        dp = [False] * (zone_size + 1)
        dp[0] = True

        for size in piece_sizes:
            for i in range(zone_size, size - 1, -1):
                dp[i] = dp[i] or dp[i - size]
        return dp[zone_size]

    def validate_solution(self, solution):
        """
        Valide si la solution actuelle couvre tout le plateau sans chevauchement.

        Paramètres:
        - solution (list): Liste des placements sélectionnés.

        Retourne:
        - bool: True si la solution est valide, False sinon.
        """
        pieces_used = set()
        cells_covered = set()

        for sol in solution:
            piece_name = sol['piece'].nom
            if piece_name in pieces_used:
                return False  # Pièce déjà utilisée.
            pieces_used.add(piece_name)

            for cell in sol['cells_covered']:
                if cell in cells_covered:
                    return False  # Chevauchement détecté.
                cells_covered.add(cell)

        all_pieces_used = len(pieces_used) == len(self.pieces)
        full_board_covered = len(cells_covered) == (self.plateau.lignes * self.plateau.colonnes)
        return all_pieces_used and full_board_covered

    def print_solution(self):
        """
        Affiche la première solution trouvée.
        """
        if not self.solutions:
            print("Aucune solution trouvée.")
            return
        print("Solution trouvée :")
        for sol in self.solutions[0]:
            piece = sol['piece']
            position = sol['position']
            print(f"Place {piece.nom} : position {position} | variante : {sol['variante_index']}")
