import itertools
import numpy as np
import time
from multiprocessing import Process, Manager
from puzzlesolver_base import *
import threading
import queue

class AlgorithmX(PuzzleSolverBase):
    """
    Classe pour gérer l'algorithme X de résolution de couverture exacte.

    ### Objectif de l'algorithme
    - Trouver une combinaison de placements de pièces qui couvre entièrement le plateau sans chevauchement.
    - Représentation du problème avec une matrice de contraintes :
        - **Lignes** : chaque ligne représente une façon possible de placer une pièce sur le plateau.
        - **Colonnes** : chaque colonne représente une contrainte à satisfaire (par exemple, couvrir une cellule spécifique du plateau ou utiliser une pièce spécifique).

    ### Flux général de résolution
    1. **Création de la matrice de contraintes** à partir des pièces et du plateau (`create_constraint_matrix`).
    2. **Lancement de l'algorithme X** pour explorer les possibilités de placement (`algorithm_x` ou `algorithm_x_parallel`).
    3. **Collecte des solutions** trouvées qui satisfont toutes les contraintes.

    ### Exemple de matrice de contraintes pour IQ Puzzler Pro

    Supposons un plateau simplifié 2x2 et deux pièces A et B :

    - **Pièce A** : forme 1x2 (horizontal).
    - **Pièce B** : forme 2x1 (vertical).

    Les positions possibles sur le plateau pour chaque pièce sont :

    - **Pièce A** :
        - Position 1 : couvre cellules (0,0) et (0,1).
        - Position 2 : couvre cellules (1,0) et (1,1).
    - **Pièce B** :
        - Position 1 : couvre cellules (0,0) et (1,0).
        - Position 2 : couvre cellules (0,1) et (1,1).

    La matrice de contraintes serait :

    |     | Cellule (0,0) | Cellule (0,1) | Cellule (1,0) | Cellule (1,1) | Pièce A | Pièce B |
    |-----|---------------|---------------|---------------|---------------|---------|---------|
    | L1  |       1       |       1       |       0       |       0       |    1    |    0    |
    | L2  |       0       |       0       |       1       |       1       |    1    |    0    |
    | L3  |       1       |       0       |       1       |       0       |    0    |    1    |
    | L4  |       0       |       1       |       0       |       1       |    0    |    1    |

    Chaque ligne représente une option de placement d'une pièce, et les 1 indiquent les contraintes satisfaites par cette option.
    """

    def __init__(self, plateau, pieces, fixed_pieces=None, update_callback=None):
        super().__init__(plateau, pieces, fixed_pieces, update_callback)
        self.solutions = []  # Liste des solutions trouvées
        self.zone_cache = {}  # Cache pour les zones vides déjà analysées
        self.invalid_placements = {}  # Cache des placements invalides
        self.solution_steps = []  # Historique des étapes de construction des solutions
        self.nbr_pieces_init = 0  # Nombre de pièces initial placé sur le plateau lors du lancement de la résolution

    def solve(self):
        """
        Point d'entrée principal pour résoudre le puzzle.

        ### Étapes principales :
        1. **Création de la matrice de contraintes** (`create_constraint_matrix`).
        2. **Lancement de l'algorithme X** (`algorithm_x_parallel` pour une version multi-processus ou `algorithm_x`).
        3. **Retour des solutions trouvées.

        ### Pseudo-code :
        ```
        Initialiser la matrice de contraintes
        Initialiser une liste vide pour la solution en cours
        Appeler l'algorithme X avec la matrice et la solution
        ```
        """
        self._stop = False
        self.nbr_pieces_init = len(self.fixed_pieces)  # Set the initial number of fixed pieces
        # Étape 1 : Création de la matrice de contraintes
        matrix, header = self.create_constraint_matrix()
        
        # Étape 2 : Lancement de l'algorithme de recherche
        solution = []
        self.algorithm_x(matrix, header, solution)
        
        # Étape 3 : Retour des solutions trouvées
        return self.solutions

    # --- Méthodes principales de l'algorithme ---
    
    def algorithm_x(self, matrix, header, solution):
        """
        Algorithme X (version séquentielle) pour la résolution du problème.

        ### Pseudo-code :
        ```
        Si toutes les contraintes sont satisfaites (matrice vide) :
            Vérifier la validité de la solution
            Ajouter la solution valide à la liste des solutions trouvées
            Retourner True

        Sélectionner la contrainte avec le moins d'options disponibles (colonne avec minimum de 1).

        Pour chaque ligne qui couvre cette contrainte :
            Ajouter la ligne à la solution
            Réduire la matrice en supprimant les colonnes couvertes et les lignes conflictuelles
            Appeler récursivement l'algorithme X
            Si une solution est trouvée, arrêter la recherche
            Sinon, effectuer un backtracking (retirer la ligne de la solution)
        ```
        """
        if self._stop:
            return False

        # Vérifie si toutes les contraintes sont satisfaites
        if self.is_solution_complete(matrix, solution):
            return True

        # Sélectionne la colonne avec le moins d'options
        column = self.select_column_with_fewest_options(matrix)
        if column is None:
            return False

        # Récupère toutes les lignes couvrant cette contrainte
        rows_to_cover = self.select_rows_covering_column(matrix, column)

        for row in rows_to_cover:
            if self._stop:
                return False

            # Ajoute la ligne à la solution actuelle
            self.try_row_in_solution(row, solution)

            # Réduit la matrice en excluant les conflits
            new_matrix = self.remove_conflicting_rows_and_columns(matrix, row)

            # Appelle récursivement l'algorithme
            if not self.has_unfillable_voids(solution):
                if self.algorithm_x(new_matrix, header, solution):
                    return True

            # Backtracking si la solution n'est pas trouvée
            self.backtrack(solution)
        return False

    # --- Méthodes pour la matrice de contraintes ---

    def create_constraint_matrix(self):
        """
        Crée une matrice de contraintes pour représenter toutes les options de placement de pièces.

        ### Explication détaillée

        - **Contraintes (colonnes)** :
            - Chaque cellule du plateau doit être couverte exactement une fois.
            - Chaque pièce doit être utilisée exactement une fois.

        - **Options (lignes)** :
            - Chaque ligne représente une façon spécifique de placer une variante d'une pièce à une position donnée.

        ### Exemple pour IQ Puzzler Pro simplifié

        Supposons un plateau 2x2 avec les pièces suivantes :

        - **Pièce A** (1x2) : peut être placée horizontalement en (0,0) ou (1,0).
        - **Pièce B** (2x1) : peut être placée verticalement en (0,0) ou (0,1).

        **Colonnes** :

        - Cellules : C0 (0,0), C1 (0,1), C2 (1,0), C3 (1,1)
        - Pièces : A, B

        **Lignes (options de placement)** :

        - **Ligne 1** : Pièce A en (0,0)
            - Couvre C0 et C1, utilise A.
        - **Ligne 2** : Pièce A en (1,0)
            - Couvre C2 et C3, utilise A.
        - **Ligne 3** : Pièce B en (0,0)
            - Couvre C0 et C2, utilise B.
        - **Ligne 4** : Pièce B en (0,1)
            - Couvre C1 et C3, utilise B.

        La matrice de contraintes est alors construite en mettant des 1 là où une option satisfait une contrainte.
        """
        total_columns, header = self.calculate_total_columns_and_create_header()
        matrix = []
        pieces_non_fixees = self.get_non_fixed_pieces()

        # Ajoute les variantes des pièces non fixées
        for piece in pieces_non_fixees:
            self.add_piece_variants_to_matrix(piece, total_columns, matrix)

        # Ajoute les pièces fixées
        self.add_fixed_pieces_to_matrix(total_columns, matrix)
        return matrix, header

    # --- Méthodes auxiliaires explicitées ---

    def is_solution_complete(self, matrix, solution):
        """
        Vérifie si toutes les contraintes sont satisfaites.

        ### Exemple d'état valide :
        - **Matrice vide** : toutes les contraintes (colonnes) sont couvertes.
        - **Solution complète** : contient les placements des pièces couvrant exactement le plateau.
        """
        if not any(row['row'] for row in matrix):
            if self.validate_solution(solution):
                self.solutions.append(solution.copy())
                self.solution_steps.append(solution.copy())
                return True
        return False

    def select_column_with_fewest_options(self, matrix):
        """
        Sélectionne la contrainte (colonne) avec le moins de lignes (options) disponibles.

        ### Exemple :
        Si la matrice contient les colonnes C0, C1, C2 avec les comptes suivants :

        - C0 : 3 options
        - C1 : 2 options
        - C2 : 1 option

        Alors, la colonne C2 sera sélectionnée car elle a le moins d'options.
        """
        if not matrix:  # Si la matrice est vide, on retourne None
            return None
        counts = [0] * len(matrix[0]['row'])
        for row in matrix:
            for idx, val in enumerate(row['row']):
                if val == 1:
                    counts[idx] += 1
        counts = [count if count > 0 else float('inf') for count in counts]
        min_count = min(counts)
        if min_count == float('inf'):
            return None
        column = counts.index(min_count)
        return column

    def select_rows_covering_column(self, matrix, column):
        """
        Récupère toutes les lignes qui couvrent une contrainte donnée.

        ### Exemple :
        Pour la colonne C2, les lignes qui ont un 1 à l'index correspondant à C2 sont sélectionnées.

        - **Supposons** que les lignes 1 et 3 couvrent C2.
        """
        rows_to_cover = [row for row in matrix if row['row'][column] == 1]
        rows_to_cover.sort(key=lambda r: -np.count_nonzero(r['piece'].forme_base))
        return rows_to_cover

    def try_row_in_solution(self, row, solution):
        """
        Ajoute une ligne à la solution actuelle.

        ### Exemple :
        Si la ligne représente le placement de la pièce A en position (1, 2), elle est ajoutée à la solution.
        """
        solution.append(row)
        self.solution_steps.append(solution.copy())
        self.placements_testes += 1
        self.update_interface(solution)

    def remove_conflicting_rows_and_columns(self, matrix, row):
        """
        Réduit la matrice en supprimant les colonnes couvertes par la ligne sélectionnée et les lignes en conflit.

        ### Étapes :
        1. **Déterminer les colonnes à supprimer** : celles où la ligne a des 1.
        2. **Construire la nouvelle matrice** en excluant :
            - Les lignes qui ont des 1 dans les colonnes à supprimer (conflits).
            - La ligne actuelle (déjà dans la solution).

        ### Exemple :
        - **Colonnes à supprimer** : indices des 1 dans la ligne sélectionnée.
        - **Nouvelles lignes** : celles qui n'ont pas de 1 dans ces colonnes.
        """
        columns_to_remove = [idx for idx, val in enumerate(row['row']) if val == 1]
        new_matrix = []
        for r in matrix:
            if r == row:
                continue
            if all(r['row'][idx] == 0 for idx in columns_to_remove):
                new_matrix.append(r)
        return new_matrix

    def backtrack(self, solution):
        """
        Effectue le backtracking en retirant la dernière ligne de la solution.

        ### Exemple :
        Si l'ajout de la pièce B en position (0,1) ne mène pas à une solution, on la retire de la solution actuelle.
        """
        solution.pop()
        self.solution_steps.pop()
        self.calculs += 1

    # --- Méthodes pour la création de la matrice de contraintes ---

    def calculate_total_columns_and_create_header(self):
        """
        Calcule le nombre total de colonnes et crée l'en-tête des colonnes.

        ### Exemple :
        Pour un plateau 2x2 (4 cellules) et 2 pièces (A, B), le total des colonnes est 6 :

        - 4 colonnes pour les cellules : C0, C1, C2, C3.
        - 2 colonnes pour les pièces : A, B.
        """
        num_cells = self.plateau.lignes * self.plateau.colonnes
        num_pieces = len(self.pieces)
        total_columns = num_cells + num_pieces
        header = ['C{}'.format(i) for i in range(num_cells)] + [piece.nom for piece in self.pieces.values()]
        return total_columns, header

    def get_non_fixed_pieces(self):
        """
        Récupère la liste des pièces non fixées, triées par nombre de variantes.

        ### Exemple :
        Si les pièces A et B sont disponibles et que B est fixée, cette méthode retournera [A].
        """
        used_pieces = set(self.fixed_pieces.keys())
        pieces_non_fixees = [piece for piece in self.pieces.values() if piece.nom not in used_pieces]
        pieces_non_fixees.sort(key=lambda p: len(p.variantes))
        return pieces_non_fixees

    def add_piece_variants_to_matrix(self, piece, total_columns, matrix):
        """
        Ajoute toutes les variantes d'une pièce non fixée à la matrice de contraintes.

        ### Étapes :
        1. Pour chaque variante de la pièce.
        2. Pour chaque position valide sur le plateau.
        3. Créer une ligne représentant ce placement (`create_row_for_variant_placement`).
        """
        num_cells = self.plateau.lignes * self.plateau.colonnes
        for variante_index, variante in enumerate(piece.variantes):
            for position in self.get_valid_positions_for_variant(variante):
                row_data = self.create_row_for_variant_placement(piece, variante_index, variante, position, total_columns, num_cells)
                matrix.append(row_data)

    def get_valid_positions_for_variant(self, variante):
        """
        Génère toutes les positions valides pour une variante sur le plateau.

        ### Exemple :
        Pour une variante de taille 1x2 sur un plateau 2x2, les positions valides sont (0,0) et (1,0).
        """
        for i in range(self.plateau.lignes):
            for j in range(self.plateau.colonnes):
                position = (i, j)
                if self.plateau.peut_placer(variante, position):
                    yield position

    def create_row_for_variant_placement(self, piece, variante_index, variante, position, total_columns, num_cells):
        """
        Crée une ligne de la matrice de contraintes pour un placement spécifique d'une variante.

        ### Paramètres :
        - **piece** : l'objet pièce en cours.
        - **variante_index** : l'index de la variante utilisée.
        - **variante** : la forme de la variante (numpy array).
        - **position** : la position (i, j) sur le plateau.
        - **total_columns** : nombre total de colonnes dans la matrice.
        - **num_cells** : nombre total de cellules du plateau.

        ### Exemple :
        Supposons que nous ayons une pièce 'A' avec une variante en forme de ligne horizontale de taille 1x2,
        et que nous voulons la placer en position (0, 0) sur un plateau 2x2.

        - **Cellules couvertes** : (0,0) et (0,1).
        - **Indices des cellules** : 0 et 1.
        - **Index de la pièce 'A'** : 4 (après les indices des cellules).

        La ligne créée aura des 1 aux indices 0, 1 et 4.
        """
        row = [0] * total_columns
        cells_covered = []
        for vi in range(variante.shape[0]):
            for vj in range(variante.shape[1]):
                if variante[vi, vj] == 1:
                    cell_index = (position[0] + vi) * self.plateau.colonnes + (position[1] + vj)
                    row[cell_index] = 1
                    cells_covered.append((position[0] + vi, position[1] + vj))
        piece_index = num_cells + list(self.pieces.keys()).index(piece.nom)
        row[piece_index] = 1
        row_data = {
            'row': row,
            'piece': piece,
            'variante_index': variante_index,
            'position': position,
            'cells_covered': cells_covered
        }
        return row_data

    def add_fixed_pieces_to_matrix(self, total_columns, matrix):
        """
        Ajoute les pièces fixées au début de la matrice de contraintes.

        ### Étapes :
        1. Pour chaque pièce fixée, créer une ligne représentant son placement spécifique.
        2. Insérer cette ligne au début de la matrice pour prioriser ces placements.
        """
        num_cells = self.plateau.lignes * self.plateau.colonnes
        for piece_name, info in self.fixed_pieces.items():
            piece = self.pieces[piece_name]
            variante_index = info['variante_index']
            position = info['position']
            variante = piece.variantes[variante_index]
            row_data = self.create_row_for_fixed_piece(piece, variante_index, variante, position, total_columns, num_cells)
            matrix.insert(0, row_data)

    def create_row_for_fixed_piece(self, piece, variante_index, variante, position, total_columns, num_cells):
        """
        Crée une ligne de la matrice de contraintes pour une pièce fixée.

        ### Exemple :
        Si la pièce 'B' est fixée en position (0,1) avec une variante verticale, cette méthode créera une ligne
        avec des 1 aux indices correspondant aux cellules couvertes et à la pièce 'B'.
        """
        row = [0] * total_columns
        cells_covered = []
        for vi in range(variante.shape[0]):
            for vj in range(variante.shape[1]):
                if variante[vi, vj] == 1:
                    cell_index = (position[0] + vi) * self.plateau.colonnes + (position[1] + vj)
                    row[cell_index] = 1
                    cells_covered.append((position[0] + vi, position[1] + vj))
        piece_index = num_cells + list(self.pieces.keys()).index(piece.nom)
        row[piece_index] = 1
        row_data = {
            'row': row,
            'piece': piece,
            'variante_index': variante_index,
            'position': position,
            'cells_covered': cells_covered,
            'fixed': True
        }
        return row_data

    # --- Méthodes pour vérifier les zones vides non comblables ---

    def has_unfillable_voids(self, solution):
        """
        Vérifie s'il existe des zones vides impossibles à remplir avec les pièces restantes.

        ### Étapes :
        1. Marquer sur un plateau temporaire les cellules couvertes par la solution actuelle.
        2. Identifier les zones vides restantes.
        3. Pour chaque zone vide, vérifier si la somme des tailles des pièces restantes peut la combler exactement.

        ### Exemple :
        Si une zone vide de taille 3 est détectée et qu'il ne reste que des pièces de tailles 2 et 4, alors la zone est non comblable.
        """
        plateau_temp = np.copy(self.plateau.plateau)
        for sol in solution:
            for cell in sol['cells_covered']:
                i, j = cell
                plateau_temp[i, j] = 1

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

            possible = self.can_fill_zone(zone_size, remaining_sizes)
            self.zone_cache[zone_size] = possible
            if not possible:
                return True
        return False

    def get_empty_zones(self, plateau_temp):
        """
        Identifie les zones vides du plateau non couvertes par les pièces.

        ### Exemple :
        Si le plateau temporaire a des zones vides de tailles différentes, cette méthode les détectera
        et les retournera sous forme de listes de coordonnées.
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
        Explore une zone vide adjacente à une cellule donnée.

        ### Exemple :
        À partir d'une cellule vide (i, j), cette méthode explore toutes les cellules adjacentes
        (haut, bas, gauche, droite) qui sont également vides, formant ainsi une zone continue.
        """
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

    def can_fill_zone(self, zone_size, remaining_sizes):
        """
        Vérifie si une zone de taille donnée peut être comblée avec les pièces restantes.

        ### Exemple :
        Si la zone a une taille de 5 et que les tailles des pièces restantes sont [2,3,4],
        cette méthode vérifiera s'il est possible de combiner des pièces pour remplir exactement la zone.
        """
        possible = False
        for i in range(1, len(remaining_sizes) + 1):
            for combo in itertools.combinations(remaining_sizes, i):
                if sum(combo) == zone_size:
                    possible = True
                    break
            if possible:
                break
        return possible

    # --- Méthode pour l'algorithme parallèle (optionnel) ---

    def algorithm_x_parallel(self, matrix, header, solution):
        """
        Version parallèle de l'algorithme X utilisant des threads pour éviter les problèmes avec tkinter.

        Paramètres :
            - matrix : matrice de contraintes actuelle
            - header : liste des noms de colonnes
            - solution : liste des placements choisis jusqu'à présent
        """
        if self._stop:
            return

        if self.is_solution_complete(matrix, solution):
            return

        column = self.select_column_with_fewest_options(matrix)
        if column is None:
            return

        rows_to_cover = self.select_rows_covering_column(matrix, column)

        # File de tâches pour collecter les solutions trouvées par les threads
        self.solution_queue = queue.Queue()
        threads = []

        for row in rows_to_cover:
            thread = threading.Thread(target=self.process_branch, args=(row, matrix, header, solution))
            thread.start()
            threads.append(thread)

        # Stocker les threads pour un arrêt ultérieur
        self.threads = threads

        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()

        # Récupérer les solutions trouvées
        while not self.solution_queue.empty():
            sol = self.solution_queue.get()
            self.solutions.append(sol)

    def process_branch(self, row, matrix, header, solution):
        """
        Traite une branche de l'algorithme en utilisant des threads.

        Paramètres :
            - row : ligne sélectionnée pour cette branche
            - matrix : matrice de contraintes actuelle
            - header : liste des noms de colonnes
            - solution : liste des placements choisis jusqu'à présent
        """
        local_solution = solution.copy()
        self.try_row_in_solution(row, local_solution)
        new_matrix = self.remove_conflicting_rows_and_columns(matrix, row)

        if not self.has_unfillable_voids(local_solution):
            self.algorithm_x(new_matrix, header, local_solution)
            # Vérifier si une solution a été trouvée
            if self.solutions:
                # Ajouter la solution à la file de tâches
                self.solution_queue.put(local_solution.copy())

        self.backtrack(local_solution)

