"""
algo x :
--------
en gros :
- on construit une matrice de contraintes pour représenter toutes les façons de placer chaque pièce (position + rotation).
- chaque ligne de la matrice décrit une possibilité pour une pièce (sa position et rotation) et couvre les cellules qu'elle occupe.
- on commence la recherche par colonne : à chaque étape, on sélectionne la colonne avec le moins d'options possibles (min contraintes) pour réduire les choix et avancer plus vite.
- une fois une pièce placée, on met à jour le plateau en bloquant les cellules couvertes et on vérifie que les zones vides restantes peuvent encore être remplies.
- si on détecte des zones vides impossibles à combler avec les pièces restantes, on coupe la branche (pruning).
- la solution est trouvée quand chaque cellule du plateau est couverte sans zones inaccessibles.
- les branches principales en parallèle testent plusieurs solutions en même temps.
- chaque processus prend une branche de départ et suit l’algorithme de manière indépendante
- pour chaque branche parallèle, on utilise un cache partagé pour éviter de recalculer les configurations déjà connues comme impossibles.
"""

import itertools
import numpy as np
import time
from multiprocessing import Process, Manager

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
        matrix, header = self.create_constraint_matrix()
        solution = []
        self.algorithm_x(matrix, header, solution)
        return self.solutions

    def create_constraint_matrix(self):
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
            for ni, nj in [(ci+1, cj), (ci-1, cj), (ci, cj+1), (ci, cj-1)]:
                if (0 <= ni < self.plateau.lignes and 0 <= nj < self.plateau.colonnes
                        and plateau_temp[ni, nj] == 0 and (ni, nj) not in visited):
                    visited.add((ni, nj))
                    queue.append((ni, nj))
                    zone.append((ni, nj))
        return zone

    def update_interface(self, solution):
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
            print("No solution.")
            return
        print("Solution Found :")
        for sol in self.solutions[0]:
            piece = sol['piece']
            position = sol['position']
            print(f"Place {piece.nom} : position {position} | variant : {sol['variante_index']}")

