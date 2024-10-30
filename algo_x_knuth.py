import itertools
import numpy as np
import time
from multiprocessing import Process, Manager

class AlgorithmX:
    """
    classe pour gérer l'algorithme x de résolution de couverture exacte en utilisant une matrice de contraintes
    """

    def __init__(self, plateau, pieces, fixed_pieces=None, update_callback=None):
        """
        initialise l'algorithme avec le plateau, les pièces et les options de configuration fixe

        paramètres :
            - plateau : objet représentant le plateau de jeu (grille)
            - pieces : dictionnaire des pièces à placer avec leurs variantes (rotations, symétries)
            - fixed_pieces : pièces déjà fixées sur le plateau (optionnel)
            - update_callback : fonction de rappel pour mettre à jour l'interface pendant la résolution (optionnel)
        """
        self.plateau = plateau  # le plateau de jeu
        self.pieces = pieces  # les pièces disponibles
        self.solutions = []  # liste des solutions trouvées
        self.fixed_pieces = fixed_pieces if fixed_pieces else {}  # pièces fixées sur le plateau
        self.update_callback = update_callback  # fonction pour mettre à jour l'interface

        self.calculs = 0  # compteur de calculs effectués
        self.placements_testes = 0  # compteur de placements testés
        self.start_time = time.time()  # temps de démarrage de l'algorithme

        self.zone_cache = {}  # cache pour les zones vides déjà calculées
        self.invalid_placements = {}  # placements invalides déjà identifiés
        self._stop = False  # indicateur pour arrêter l'algorithme

        self.solution_steps = []  # étapes de la solution en cours

    def stop(self):
        """
        stoppe le processus de résolution
        """
        self._stop = True

    def solve(self):
        """
        démarre la résolution en créant la matrice de contraintes et en lançant l'algorithme

        retourne :
            - self.solutions : liste des solutions trouvées
        """
        self._stop = False
        matrix, header = self.create_constraint_matrix()  # création de la matrice de contraintes
        solution = []  # initialisation de la solution
        self.algorithm_x(matrix, header, solution)  # lancement de l'algorithme x
        return self.solutions

    def create_constraint_matrix(self):
        """
        crée la matrice de contraintes pour chaque variante possible de chaque pièce

        retourne :
            - matrix : matrice de contraintes avec chaque ligne représentant une option de placement
            - header : liste des noms de colonnes, couvrant chaque cellule du plateau et chaque pièce
        """
        num_cells = self.plateau.lignes * self.plateau.colonnes  # nombre total de cellules du plateau
        num_pieces = len(self.pieces)  # nombre total de pièces
        total_columns = num_cells + num_pieces  # total des colonnes (cellules + pièces)

        # création de l'en-tête des colonnes (cellules du plateau et pièces)
        header = ['C{}'.format(i) for i in range(num_cells)] + [piece.nom for piece in self.pieces.values()]
        matrix = []  # initialisation de la matrice de contraintes
        used_pieces = set(self.fixed_pieces.keys())  # pièces déjà utilisées (fixées)
        # liste des pièces non fixées, triées par nombre de variantes pour optimiser la recherche
        pieces_non_fixees = [piece for piece in self.pieces.values() if piece.nom not in used_pieces]
        pieces_non_fixees.sort(key=lambda p: len(p.variantes))

        # pour chaque pièce non fixée
        for piece in pieces_non_fixees:
            # pour chaque variante de la pièce (rotation, symétrie)
            for variante_index, variante in enumerate(piece.variantes):
                # pour chaque position possible sur le plateau
                for i in range(self.plateau.lignes):
                    for j in range(self.plateau.colonnes):
                        position = (i, j)
                        # vérifie si la variante peut être placée à cette position
                        if self.plateau.peut_placer(variante, position):
                            row = [0] * total_columns  # initialise une ligne de la matrice
                            cells_covered = []  # liste des cellules couvertes par cette variante
                            # parcourt les cellules de la variante
                            for vi in range(variante.shape[0]):
                                for vj in range(variante.shape[1]):
                                    if variante[vi, vj] == 1:
                                        # calcule l'index de la cellule sur le plateau
                                        cell_index = (i + vi) * self.plateau.colonnes + (j + vj)
                                        row[cell_index] = 1  # marque la cellule comme couverte
                                        cells_covered.append((i + vi, j + vj))  # ajoute la cellule à la liste
                            # marque la pièce comme utilisée dans cette ligne
                            piece_index = num_cells + list(self.pieces.keys()).index(piece.nom)
                            row[piece_index] = 1
                            # ajoute la ligne à la matrice
                            matrix.append({
                                'row': row,
                                'piece': piece,
                                'variante_index': variante_index,
                                'position': position,
                                'cells_covered': cells_covered
                            })

        # pour les pièces fixées, on les ajoute en début de matrice
        for piece_name, info in self.fixed_pieces.items():
            piece = self.pieces[piece_name]
            variante_index = info['variante_index']
            position = info['position']
            variante = piece.variantes[variante_index]

            row = [0] * total_columns  # initialise une ligne de la matrice
            cells_covered = []  # liste des cellules couvertes par cette variante
            # parcourt les cellules de la variante
            for vi in range(variante.shape[0]):
                for vj in range(variante.shape[1]):
                    if variante[vi, vj] == 1:
                        # calcule l'index de la cellule sur le plateau
                        cell_index = (position[0] + vi) * self.plateau.colonnes + (position[1] + vj)
                        row[cell_index] = 1  # marque la cellule comme couverte
                        cells_covered.append((position[0] + vi, position[1] + vj))  # ajoute la cellule à la liste
            # marque la pièce comme utilisée dans cette ligne
            piece_index = num_cells + list(self.pieces.keys()).index(piece_name)
            row[piece_index] = 1
            # insère la ligne au début de la matrice pour prioriser les pièces fixées
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
        """
        implémente l'algorithme x pour trouver une solution de couverture exacte

        paramètres :
            - matrix : matrice de contraintes actuelle
            - header : liste des noms de colonnes
            - solution : liste des placements choisis jusqu'à présent

        retourne :
            - True si une solution est trouvée, False sinon
        """
        if self._stop:
            return False
        # si la matrice est vide, toutes les contraintes sont satisfaites
        if not any(row['row'] for row in matrix):
            if self.validate_solution(solution):  # vérifie si la solution est valide
                self.solutions.append(solution.copy())  # ajoute la solution aux solutions trouvées
                self.solution_steps.append(solution.copy())  # enregistre l'étape de la solution
                return True
            return False

        # compte le nombre d'options pour chaque colonne (minimum de contraintes)
        counts = [0] * len(header)
        for row in matrix:
            for idx, val in enumerate(row['row']):
                if val == 1:
                    counts[idx] += 1

        # ignore les colonnes déjà couvertes
        counts = [count if any(row['row'][idx] == 1 for row in matrix) else float('inf') for idx, count in enumerate(counts)]
        min_count = min(counts)
        if min_count == float('inf'):
            return False

        # choisit la colonne avec le moins d'options
        column = counts.index(min_count)
        # sélectionne les lignes qui couvrent cette colonne
        rows_to_cover = [row for row in matrix if row['row'][column] == 1]

        # trie les lignes pour optimiser la recherche (pièces les plus grandes en premier)
        rows_to_cover.sort(key=lambda r: -np.count_nonzero(r['piece'].forme_base))

        # pour chaque ligne possible
        for row in rows_to_cover:
            if self._stop:
                return False
            solution.append(row)  # ajoute la ligne à la solution
            self.solution_steps.append(solution.copy())  # enregistre l'étape
            self.placements_testes += 1  # incrémente le compteur

            self.update_interface(solution)  # met à jour l'interface si nécessaire

            # détermine les colonnes à supprimer
            columns_to_remove = [idx for idx, val in enumerate(row['row']) if val == 1]
            new_matrix = []
            # construit la nouvelle matrice en excluant les lignes en conflit
            for r in matrix:
                if r == row:
                    continue
                if all(r['row'][idx] == 0 for idx in columns_to_remove):
                    new_matrix.append(r)

            # vérifie s'il n'y a pas de zones vides impossibles à remplir
            if not self.has_unfillable_voids(solution):
                if self.algorithm_x(new_matrix, header, solution):  # appel récursif
                    return True

            solution.pop()  # retire la ligne de la solution
            self.solution_steps.pop()
            self.calculs += 1  # incrémente le compteur de calculs
        return False

    def algorithm_x_parallel(self, matrix, header, solution):
        """
        version parallèle de l'algorithme x pour exploiter le multiprocesseur

        paramètres :
            - matrix : matrice de contraintes actuelle
            - header : liste des noms de colonnes
            - solution : liste des placements choisis jusqu'à présent
        """
        if self._stop:
            return False
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
        """
        traite une branche de l'algorithme en parallèle

        paramètres :
            - row : ligne sélectionnée pour cette branche
            - matrix : matrice de contraintes actuelle
            - header : liste des noms de colonnes
            - solution : liste des placements choisis jusqu'à présent
        """
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
        """
        vérifie s'il existe des zones vides impossibles à remplir avec les pièces restantes

        paramètres :
            - solution : liste des placements choisis jusqu'à présent

        retourne :
            - True si des zones vides non comblables sont détectées, False sinon
        """
        # copie temporaire du plateau
        plateau_temp = np.copy(self.plateau.plateau)
        # marque les cellules déjà couvertes par la solution actuelle
        for sol in solution:
            for cell in sol['cells_covered']:
                i, j = cell
                plateau_temp[i, j] = 1

        # obtient les zones vides restantes
        empty_zones = self.get_empty_zones(plateau_temp)
        # pièces restantes à placer
        remaining_pieces = set(self.pieces.keys()) - set(sol['piece'].nom for sol in solution)
        # tailles des pièces restantes
        remaining_sizes = [np.count_nonzero(self.pieces[piece_name].forme_base) for piece_name in remaining_pieces]

        # pour chaque zone vide
        for zone in empty_zones:
            zone_size = len(zone)
            # vérifie si la zone a déjà été traitée
            if zone_size in self.zone_cache:
                if not self.zone_cache[zone_size]:
                    return True
                else:
                    continue

            possible = False
            # vérifie si la somme des tailles des pièces restantes peut combler la zone
            for i in range(1, len(remaining_sizes)+1):
                for combo in itertools.combinations(remaining_sizes, i):
                    if sum(combo) == zone_size:
                        possible = True
                        break
                if possible:
                    break
            self.zone_cache[zone_size] = possible  # met à jour le cache
            if not possible:
                return True
        return False

    def get_empty_zones(self, plateau_temp):
        """
        identifie les zones vides du plateau non couvertes par les pièces

        paramètres :
            - plateau_temp : plateau temporaire avec les cellules couvertes

        retourne :
            - empty_zones : liste des zones vides identifiées
        """
        visited = set()  # cellules déjà visitées
        empty_zones = []  # liste des zones vides
        # parcourt chaque cellule du plateau
        for i in range(self.plateau.lignes):
            for j in range(self.plateau.colonnes):
                # si la cellule est vide et non visitée
                if plateau_temp[i, j] == 0 and (i, j) not in visited:
                    zone = self.explore_zone(plateau_temp, i, j, visited)  # explore la zone
                    empty_zones.append(zone)  # ajoute la zone à la liste
        return empty_zones

    def explore_zone(self, plateau_temp, i, j, visited):
        """
        explore une zone vide adjacente à une cellule donnée

        paramètres :
            - plateau_temp : plateau temporaire avec les cellules couvertes
            - i, j : coordonnées de la cellule de départ
            - visited : ensemble des cellules déjà visitées

        retourne :
            - zone : liste des cellules appartenant à la zone vide
        """
        queue = [(i, j)]  # file d'attente pour le parcours en largeur
        visited.add((i, j))  # marque la cellule comme visitée
        zone = [(i, j)]  # initialise la zone

        # tant qu'il y a des cellules à explorer
        while queue:
            ci, cj = queue.pop(0)  # récupère la cellule courante
            # vérifie les cellules adjacentes (haut, bas, gauche, droite)
            for ni, nj in [(ci+1, cj), (ci-1, cj), (ci, cj+1), (ci, cj-1)]:
                # si la cellule est dans les limites du plateau, vide et non visitée
                if (0 <= ni < self.plateau.lignes and 0 <= nj < self.plateau.colonnes
                        and plateau_temp[ni, nj] == 0 and (ni, nj) not in visited):
                    visited.add((ni, nj))  # marque la cellule comme visitée
                    queue.append((ni, nj))  # ajoute la cellule à la file d'attente
                    zone.append((ni, nj))  # ajoute la cellule à la zone
        return zone

    def update_interface(self, solution):
        """
        met à jour l'interface utilisateur avec les informations actuelles de la résolution

        paramètres :
            - solution : liste des placements choisis jusqu'à présent
        """
        if self.update_callback:
            elapsed_time = time.time() - self.start_time  # calcule le temps écoulé
            stats = {
                "time": elapsed_time,
                "calculs": self.calculs,
                "placements_testes": self.placements_testes,
                "solution": solution
            }
            self.update_callback(stats)  # appelle la fonction de mise à jour

    def validate_solution(self, solution):
        """
        vérifie si la solution actuelle est valide (toutes les pièces placées sans chevauchement)

        paramètres :
            - solution : liste des placements choisis jusqu'à présent

        retourne :
            - True si la solution est valide, False sinon
        """
        pieces_used = set()  # ensemble des pièces utilisées
        cells_covered = set()  # ensemble des cellules couvertes

        # pour chaque placement dans la solution
        for sol in solution:
            piece_name = sol['piece'].nom
            if piece_name in pieces_used:
                return False  # pièce déjà utilisée
            pieces_used.add(piece_name)

            # vérifie les cellules couvertes
            for cell in sol['cells_covered']:
                if cell in cells_covered:
                    return False  # cellule déjà couverte
                cells_covered.add(cell)

        all_pieces_used = len(pieces_used) == len(self.pieces)  # toutes les pièces sont utilisées
        full_board_covered = len(cells_covered) == (self.plateau.lignes * self.plateau.colonnes)  # le plateau est entièrement couvert
        return all_pieces_used and full_board_covered

    def print_solution(self):
        """
        affiche la première solution trouvée
        """
        if not self.solutions:
            print("aucune solution trouvée.")
            return
        print("solution trouvée :")
        for sol in self.solutions[0]:
            piece = sol['piece']
            position = sol['position']
            print(f"placer {piece.nom} : position {position} | variante : {sol['variante_index']}")
