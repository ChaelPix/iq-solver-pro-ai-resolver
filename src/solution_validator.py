
class SolutionValidator:
    """
    Classe responsable de la validation finale d'une solution.
    Une solution est valide si:
    - Toutes les pièces sont utilisées exactement une fois.
    - Toutes les cellules du plateau sont couvertes sans chevauchement.
    """
    def __init__(self, pieces, plateau):
        self.pieces = pieces
        self.plateau = plateau

    def validate_solution(self, solution):
        """
        Valide la solution:
        1. Vérifie que chaque pièce est utilisée une seule fois.
        2. Vérifie qu'aucune cellule n'est couverte par deux pièces (pas de chevauchement).
        3. Vérifie que toutes les cellules du plateau sont couvertes (solution complète).

        Paramètres:
        - solution (list): Liste des placements (chaque placement contient 'piece', 'cells_covered', etc.)

        Retourne:
        - bool: True si la solution est valide, False sinon.
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