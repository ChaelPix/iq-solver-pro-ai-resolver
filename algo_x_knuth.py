import time
import numpy as np

class InterfaceBridge:
    """
    Classe mère pour la gestion des statistiques.
    Ne dépend plus d'un callback externe.
    Les stats sont stockées localement et accessibles par un getter.
    """

    def __init__(self, branch_id="main"):
        """
        Initialise la gestion des statistiques.
        
        Paramètres:
        - branch_id (str): Identifiant de la branche (thread) de recherche.
        """
        self.branch_id = branch_id
        self.calculs = 0  # Nombre total de calculs effectués.
        self.placements_testes = 0  # Nombre de placements testés.
        self.start_time = time.time()  # Temps de démarrage de l'algorithme.
        self.stop_requested = False  # Drapeau pour arrêter l'algorithme.
        self.solution_steps = []  # Liste pour stocker les étapes de la solution.

        # Nouvelles statistiques
        self.branches_explored = 0  # Nombre de branches explorées.
        self.branches_pruned = 0  # Nombre de branches coupées.
        self.max_recursion_depth = 0  # Profondeur maximale de récursion.
        self.current_recursion_depth = 0  # Profondeur actuelle de récursion.

        # Stockage local des stats
        self._stats_data = {}

    def update_interface(self, solution):
        """
        Met à jour les statistiques localement.
        
        Paramètres:
        - solution (list): Liste actuelle des placements de pièces.
        """
        elapsed_time = time.time() - self.start_time
        self._stats_data = {
            "branch_id": self.branch_id,
            "time": elapsed_time,
            "calculs": self.calculs,
            "placements_testes": self.placements_testes,
            "solution": solution.copy(),
            "branches_explored": self.branches_explored,
            "branches_pruned": self.branches_pruned,
            "max_recursion_depth": self.max_recursion_depth
        }

    def request_stop(self):
        """
        Demande l'arrêt de l'algorithme.
        """
        self.stop_requested = True

    def get_solution_steps(self):
        """
        Retourne les étapes de la solution finale.
        """
        return self.solution_steps.copy()

    def get_stats_data(self):
        """
        Retourne les données de statistiques.
        """
        return self._stats_data.copy()

class AlgorithmX(InterfaceBridge):
    """
    Implémente l'algorithme X de Knuth pour résoudre un problème de couverture exacte.
    Gère les stats localement sans callbacks.
    Peut être utilisé en multithreading (branch_id différent, etc.).
    """

    def __init__(self, plateau, pieces, heuristic_ascender, fixed_pieces=None, branch_id="main"):
        """
        Initialise l'algorithme avec le plateau, les pièces, l'heuristique et les pièces fixes.
        
        Paramètres:
        - plateau (Plateau)
        - pieces (dict)
        - heuristic_ascender (bool): True si heuristique ascendante, False sinon.
        - fixed_pieces (dict): Pièces déjà placées
        - branch_id (str): Identifiant de la branche (thread) de recherche.
        """
        super().__init__(branch_id=branch_id)
        self.plateau = plateau
        self.pieces = pieces
        self.fixed_pieces = fixed_pieces if fixed_pieces else {}
        self.solutions = []
        self.zone_cache = {}
        self.invalid_placements = {}

        # Calcul du poids des pièces pour l'heuristique
        self.piece_weights = self.calculate_piece_weights(heuristic_ascender)

    def calculate_piece_weights(self, heuristic_ascender):
        weights = {}
        for piece in self.pieces.values():
            if not hasattr(piece, 'forme_base') or piece.forme_base is None:
                weights[piece.nom] = float('inf')
                continue

            occupied_cells = np.count_nonzero(piece.forme_base)
            if occupied_cells == 0:
                weights[piece.nom] = float('inf')
            else:
                if heuristic_ascender:
                    weights[piece.nom] = 1 / occupied_cells
                else:
                    weights[piece.nom] = occupied_cells
        return weights

    def solve(self):
        """
        Lance la résolution du problème en utilisant l'algorithme X.
        Les solutions trouvées sont stockées localement.
        """
        matrix, header = self.create_constraint_matrix()
        solution = []
        self.algorithm_x(matrix, header, solution)
        return self.solutions

    def create_constraint_matrix(self):
        # Création de la matrice de contraintes
        num_cells = self.plateau.lignes * self.plateau.colonnes
        num_pieces = len(self.pieces)
        total_columns = num_cells + num_pieces

        header = ['C{}'.format(i) for i in range(num_cells)] + [piece.nom for piece in self.pieces.values()]

        matrix = []
        used_pieces = set(self.fixed_pieces.keys())

        # Pièces non fixées triées par l'heuristique
        pieces_non_fixees = [p for p in self.pieces.values() if p.nom not in used_pieces]
        pieces_non_fixees.sort(key=lambda p: -self.piece_weights[p.nom])

        for piece in pieces_non_fixees:
            self.add_piece_to_matrix(piece, matrix, num_cells)

        for piece_name, info in self.fixed_pieces.items():
            piece = self.pieces[piece_name]
            self.add_fixed_piece_to_matrix(piece, info, matrix, num_cells)

        return matrix, header

    def add_piece_to_matrix(self, piece, matrix, num_cells):
        for variante_index, variante in enumerate(piece.variantes):
            for i in range(self.plateau.lignes):
                for j in range(self.plateau.colonnes):
                    if self.plateau.peut_placer(variante, (i, j)):
                        row, cells_covered = self.create_row_for_placement(piece, variante, (i, j), num_cells)
                        piece_index = num_cells + list(self.pieces.keys()).index(piece.nom)
                        row[piece_index] = 1
                        matrix.append({
                            'row': row,
                            'piece': piece,
                            'variante_index': variante_index,
                            'position': (i, j),
                            'cells_covered': cells_covered
                        })

    def add_fixed_piece_to_matrix(self, piece, info, matrix, num_cells):
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
        total_columns = num_cells + len(self.pieces)
        row = [0] * total_columns
        cells_covered = []

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
        if self.stop_requested:
            return False

        self.branches_explored += 1
        self.current_recursion_depth += 1
        if self.current_recursion_depth > self.max_recursion_depth:
            self.max_recursion_depth = self.current_recursion_depth

        if not matrix:
            if self.validate_solution(solution):
                self.solutions.append(solution.copy())
                self.solution_steps = solution.copy()
                self.current_recursion_depth -= 1
                return True
            self.current_recursion_depth -= 1
            return False

        column = self.select_min_column(matrix, header)
        if column is None:
            self.current_recursion_depth -= 1
            return False

        rows_to_cover = [row for row in matrix if row['row'][column] == 1]
        rows_to_cover = self.prioritize_rows(rows_to_cover)

        for row in rows_to_cover:
            if self.stop_requested:
                self.current_recursion_depth -= 1
                return False

            solution.append(row)
            self.placements_testes += 1
            # On met à jour les stats localement
            self.update_interface(solution)

            columns_to_remove = [idx for idx, val in enumerate(row['row']) if val == 1]
            new_matrix = self.cover_columns(matrix, columns_to_remove, row)

            if not self.has_unfillable_voids(solution):
                if self.algorithm_x(new_matrix, header, solution):
                    self.current_recursion_depth -= 1
                    return True
            else:
                self.branches_pruned += 1

            solution.pop()
            self.calculs += 1

        self.current_recursion_depth -= 1
        return False

    def select_min_column(self, matrix, header):
        counts = [0] * len(header)
        for r in matrix:
            for idx, val in enumerate(r['row']):
                if val == 1:
                    counts[idx] += 1

        counts = [count if count > 0 else float('inf') for count in counts]
        min_count = min(counts)
        if min_count == float('inf'):
            return None
        column = counts.index(min_count)
        return column

    def prioritize_rows(self, rows):
        rows.sort(key=lambda r: -self.piece_weights[r['piece'].nom])
        return rows

    def cover_columns(self, matrix, columns_to_remove, selected_row):
        new_matrix = []
        for r in matrix:
            if r == selected_row:
                continue
            if all(r['row'][idx] == 0 for idx in columns_to_remove):
                new_matrix.append(r)
        return new_matrix

    def has_unfillable_voids(self, solution):
        plateau_temp = self.apply_solution_to_plateau(solution)
        empty_zones = self.get_empty_zones(plateau_temp)
        remaining_pieces = set(self.pieces.keys()) - set(sol['piece'].nom for sol in solution)
        remaining_sizes = [np.count_nonzero(self.pieces[p].forme_base) for p in remaining_pieces]

        for zone in empty_zones:
            zone_size = len(zone)
            if zone_size in self.zone_cache:
                if not self.zone_cache[zone_size]:
                    return True
                else:
                    continue

            possible = self.is_zone_fillable(zone_size, remaining_sizes)
            self.zone_cache[zone_size] = possible
            if not possible:
                return True
        return False

    def apply_solution_to_plateau(self, solution):
        plateau_temp = np.copy(self.plateau.plateau)
        for sol in solution:
            for cell in sol['cells_covered']:
                i, j = cell
                plateau_temp[i, j] = 1
        return plateau_temp

    def get_empty_zones(self, plateau_temp):
        visited = set()
        empty_zones = []
        for i in range(self.plateau.lignes):
            for j in range(self.plateau.colonnes):
                if plateau_temp[i, j] == 0 and (i, j) not in visited:
                    zone = self.explore_zone(plateau_temp, i, j, visited)
                    empty_zones.append(zone)
        return empty_zones

    def explore_zone(self, plateau_temp, i, j, visited):
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
        return [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]

    def is_zone_fillable(self, zone_size, remaining_sizes):
        return self.can_fill_zone(zone_size, remaining_sizes)

    def can_fill_zone(self, zone_size, piece_sizes):
        dp = [False] * (zone_size + 1)
        dp[0] = True

        for size in piece_sizes:
            for i in range(zone_size, size - 1, -1):
                dp[i] = dp[i] or dp[i - size]
        return dp[zone_size]

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
