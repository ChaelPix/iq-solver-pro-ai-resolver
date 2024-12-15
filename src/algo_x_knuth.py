from algorithm_stats import AlgorithmStats
from constraint_matrix_builder import ConstraintMatrixBuilder
from zone_checker import ZoneChecker
from solution_validator import SolutionValidator
import numpy as np

class AlgorithmX:
    """
    Implémentation de l'algorithme X de Knuth pour résoudre un problème de couverture exacte.
    Cet algorithme utilise une structure de backtracking, en sélectionnant à chaque étape
    la colonne la plus contrainte (MRV heuristic), puis en essayant chacun des placements correspondants.

    Ajouts dans cette version:
    - Séparation des responsabilités en plusieurs classes (pour la matrice, la validation, etc.).
    - Statistiques avancées (branches explorées, prunings, profondeur, temps).
    - Suppression de dépendances à une interface graphique.
    - Possibilité de stopper l'algorithme via request_stop().

    Paramètres:
    - plateau (Plateau): Plateau du puzzle.
    - pieces (dict): Dictionnaire {nom: Piece} de toutes les pièces.
    - heuristic_ascender (bool): Choix d'heuristique sur les poids des pièces.
      True: pièces plus "petites" prioritaires. False: pièces plus "grandes" prioritaires.
    - fixed_pieces (dict): Pièces déjà placées (variante et position), optionnel.
    """
    def __init__(self, plateau, pieces, heuristic="ascender", fixed_pieces=None):
        self.plateau = plateau
        self.pieces = pieces
        self.fixed_pieces = fixed_pieces if fixed_pieces else {}
        self.solutions = []
        self.zone_cache = {}
        self.invalid_placements = {}
        self.stop_requested = False
        self.piece_weights = self.calculate_piece_weights(heuristic)
        self.stats = AlgorithmStats()
        self.stats.reset_stats()
        self.stats.start_timer()

    def request_stop(self):
        """
        Demande l'arrêt de l'algorithme (le stop sera pris en compte dans la prochaine itération).
        """
        self.stop_requested = True

    def get_stats(self):
        """
        Retourne les statistiques actuelles de l'algorithme.
        Peut être appelé pendant l'exécution pour avoir un suivi.

        Retourne:
        - dict: Dictionnaire de statistiques.
        """
        return self.stats.get_stats()

    def get_current_solution_steps(self):
        """
        Retourne les étapes de la dernière solution trouvée.
        Chaque étape est un placement de pièce.
        """
        return self.stats.get_current_solution_steps()

    def get_solutions(self):
        """
        Retourne la liste complète des solutions trouvées.
        """
        return self.solutions.copy()

    def calculate_piece_weights(self, heuristic="ascender"):
        """
        Calcule les poids des pièces en fonction de l'heuristique choisie.
        Les heuristiques permettent de prioriser l'ordre de placement des pièces
        en fonction de leur forme, taille ou d'autres critères.

        - "ascender": Priorité aux petites pièces.
        - "descender": Priorité aux grandes pièces.
        - "compactness": Priorité aux pièces compactes.
        - "compactness_inverse": Priorité aux pièces non compactes (grandes disparités largeur/hauteur).
        - "perimeter": Priorité aux petits périmètres.
        - "perimeter_inverse": Priorité aux grands périmètres.
        - "holes": Priorité aux pièces avec peu de trous internes.
        - "holes_inverse": Priorité aux pièces avec plus de trous internes.

        Paramètres:
        - heuristic (str): Nom de l'heuristique à utiliser.

        Retourne:
        - dict: Dictionnaire des poids des pièces, {nom_piece: poids}.
        """
        weights = {}

        for piece in self.pieces.values():
            if not hasattr(piece, 'forme_base') or piece.forme_base is None:
                weights[piece.nom] = float('inf')
                continue

            occupied_cells = np.count_nonzero(piece.forme_base)  # Nombre de cellules occupées.
            if occupied_cells == 0:
                weights[piece.nom] = float('inf')
                continue

            # Calcul des critères nécessaires pour les heuristiques
            shape = piece.forme_base
            height, width = shape.shape
            compactness = min(height, width) / max(height, width)  # Ratio compact.
            perimeter = np.sum(np.pad(shape, pad_width=1, mode='constant', constant_values=0) != 0) - occupied_cells
            holes = np.sum(shape == 0)  # Zones vides dans la forme.

            if heuristic == "ascender":
                weights[piece.nom] = 1 / occupied_cells  # Priorité aux petites pièces.
            elif heuristic == "descender":
                weights[piece.nom] = occupied_cells  # Priorité aux grandes pièces.
            elif heuristic == "compactness":
                weights[piece.nom] = compactness  # Priorité aux pièces compactes.
            elif heuristic == "compactness_inverse":
                weights[piece.nom] = 1 / (compactness + 1e-6)  # Priorité aux pièces non compactes.
            elif heuristic == "perimeter":
                weights[piece.nom] = 1 / perimeter if perimeter > 0 else float('inf')  # Priorité aux petits périmètres.
            elif heuristic == "perimeter_inverse":
                weights[piece.nom] = perimeter  # Priorité aux grands périmètres.
            elif heuristic == "holes":
                weights[piece.nom] = 1 / (holes + 1)  # Priorité aux pièces avec peu de trous.
            elif heuristic == "holes_inverse":
                weights[piece.nom] = holes  # Priorité aux pièces avec plus de trous.
            else:
                raise ValueError(f"Unknown heuristic: {heuristic}")

        return weights



    def solve(self):
        """
        Lance le processus de résolution en construisant la matrice de contraintes,
        puis en appelant la méthode algorithm_x pour parcourir les possibilités.

        Retourne:
        - solutions (list): Liste des solutions complètes trouvées.
        """
        builder = ConstraintMatrixBuilder(self.plateau, self.pieces, self.piece_weights, self.fixed_pieces)
        matrix, header = builder.create_constraint_matrix()
        solution = []
        self.algorithm_x(matrix, header, solution)
        return self.solutions

    def algorithm_x(self, matrix, header, solution):
        """
        Méthode récursive qui implémente l'algorithme X:
        1. Si la matrice est vide, on valide la solution. Si valide, on la stocke.
        2. Sinon, on choisit la colonne la plus contraignante (peu d'options).
        3. Pour chaque ligne (placement) qui couvre cette colonne, on sélectionne
           ce placement, on met à jour la matrice (on "couvre" les colonnes correspondantes),
           puis on appelle récursivement algorithm_x.
        4. Si l'on trouve une solution complète, on peut s'arrêter ou continuer
           pour trouver toutes les solutions (selon les besoins).

        Paramètres:
        - matrix (list): Matrice actuelle de contraintes.
        - header (list): En-tête de la matrice (nom des colonnes).
        - solution (list): Liste des placements choisis jusqu'ici.

        Retourne:
        - bool: True si une solution a été trouvée, False sinon.
        """
        if self.stop_requested:
            return False
        self.stats.increment_branches_explored()
        self.stats.increment_depth()

        if not matrix:
            validator = SolutionValidator(self.pieces, self.plateau)
            if validator.validate_solution(solution):
                self.solutions.append(solution.copy())
                self.stats.add_solution(solution)
                self.stats.decrement_depth()
                self.stats.stop_timer()
                return True
            self.stats.decrement_depth()
            return False

        column = self.select_min_column(matrix, header)
        if column is None:
            self.stats.decrement_depth()
            return False

        rows_to_cover = [row for row in matrix if row['row'][column] == 1]
        rows_to_cover = self.prioritize_rows(rows_to_cover)

        checker = ZoneChecker(self.plateau, self.pieces, self.zone_cache)

        for row in rows_to_cover:
            if self.stop_requested:
                self.stats.decrement_depth()
                return False

            solution.append(row)
            self.stats.set_current_solution_steps(solution)
            self.stats.increment_placements_testes()

            columns_to_remove = [idx for idx, val in enumerate(row['row']) if val == 1]
            new_matrix = self.cover_columns(matrix, columns_to_remove, row)

            # Vérification des zones vides résiduelles (pruning)
            if not checker.has_unfillable_voids(solution):
                if self.algorithm_x(new_matrix, header, solution):
                    self.stats.decrement_depth()
                    return True
            else:
                self.stats.increment_branches_pruned()

            solution.pop()
            self.stats.increment_calculs()

        self.stats.decrement_depth()
        return False

    def select_min_column(self, matrix, header):
        """
        Sélectionne la colonne avec le moins d'options (heuristique MRV - Minimum Remaining Values).
        On compte pour chaque colonne le nombre de lignes (placements) qui la couvrent.
        La colonne avec le moins d'options est choisie car plus contraignante,
        réduisant l'espace de recherche.

        Paramètres:
        - matrix (list): Matrice de contraintes
        - header (list): Noms des colonnes (non utilisé directement ici)

        Retourne:
        - int ou None: L'indice de colonne choisie, ou None si aucune (matrice vide).
        """
        counts = [0] * len(header)
        for row in matrix:
            for idx, val in enumerate(row['row']):
                if val == 1:
                    counts[idx] += 1
        counts = [c if c > 0 else float('inf') for c in counts]
        m = min(counts)
        if m == float('inf'):
            return None
        return counts.index(m)

    def prioritize_rows(self, rows):
        """
        Priorise les lignes (placements) en fonction de l'heuristique de poids sur les pièces.
        Ici, on tri en ordre décroissant de poids.
        Les pièces avec un poids plus grand seront considérées en premier.

        Paramètres:
        - rows (list): Lignes candidates couvrant la colonne choisie.

        Retourne:
        - rows (list): Lignes triées selon la priorité.
        """
        rows.sort(key=lambda r: -self.piece_weights[r['piece'].nom])
        return rows

    def cover_columns(self, matrix, columns_to_remove, selected_row):
        """
        Met à jour la matrice après avoir sélectionné un placement.
        On retire toutes les lignes qui couvrent les mêmes colonnes pour maintenir la cohérence.

        Paramètres:
        - matrix (list): Matrice de contraintes actuelle
        - columns_to_remove (list): Liste des indices de colonnes couvertes par le placement choisi
        - selected_row (dict): Le placement choisi

        Retourne:
        - new_matrix (list): Nouvelle matrice réduite.
        """
        new_matrix = []
        for r in matrix:
            if r == selected_row:
                continue
            if all(r['row'][idx] == 0 for idx in columns_to_remove):
                new_matrix.append(r)
        return new_matrix
