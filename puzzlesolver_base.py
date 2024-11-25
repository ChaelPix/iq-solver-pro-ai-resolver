import itertools
import numpy as np
import time
from multiprocessing import Process, Manager


class PuzzleSolverBase:
    """
    Classe de base pour les solveurs de puzzles.
    Contient des méthodes génériques utiles pour différents algorithmes de résolution.
    """
    def __init__(self, plateau, pieces, fixed_pieces=None, update_callback=None):
        self.plateau = plateau
        self.pieces = pieces
        self.fixed_pieces = fixed_pieces if fixed_pieces else {}
        self.update_callback = update_callback
        self.start_time = time.time()
        self.calculs = 0
        self.placements_testes = 0
        self._stop = False

    def stop(self):
        """Stoppe le processus de résolution."""
        self._stop = True

    def update_interface(self, solution):
        """
        Met à jour l'interface utilisateur avec les informations actuelles de la résolution.

        Paramètres :
            - solution : liste des placements choisis jusqu'à présent
        """
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
        """
        Vérifie si la solution actuelle est valide (toutes les pièces placées sans chevauchement).

        Paramètres :
            - solution : liste des placements choisis jusqu'à présent

        Retourne :
            - True si la solution est valide, False sinon
        """
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
        """Affiche la première solution trouvée."""
        if not self.solutions:
            print("Aucune solution trouvée.")
            return
        print("Solution trouvée :")
        for sol in self.solutions[0]:
            piece = sol['piece']
            position = sol['position']
            print(f"Placer {piece.nom} : position {position} | variante : {sol['variante_index']}")