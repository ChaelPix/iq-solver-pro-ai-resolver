import numpy as np

class ConstraintMatrixBuilder:
    """
    Classe responsable de la construction de la matrice de contraintes pour l'algorithme X.
    Cette matrice combine les contraintes spatiales (couvrir chaque cellule du plateau)
    et les contraintes de ressources (chaque pièce doit être placée une seule fois).

    Paramètres:
    - plateau: Objet représentant le plateau (avec .lignes, .colonnes et .plateau)
    - pieces (dict): Dictionnaire {nom: piece}, chaque pièce contenant ses variantes et sa forme.
    - piece_weights (dict): Poids associés aux pièces pour guider l'heuristique.
    - fixed_pieces (dict): Pièces fixées à des positions et variantes précises.

    La matrice de contraintes est un tableau de dictionnaires.
    Chaque entrée représente un placement potentiel d'une pièce sur le plateau.
    """
    def __init__(self, plateau, pieces, piece_weights, fixed_pieces):
        self.plateau = plateau
        self.pieces = pieces
        self.piece_weights = piece_weights
        self.fixed_pieces = fixed_pieces

    def create_constraint_matrix(self):
        """
        Crée la matrice de contraintes nécessaire à l'algorithme X.
        On distingue les colonnes correspondant aux cellules du plateau et
        les colonnes correspondant aux pièces.

        Retourne:
        - matrix (list): La liste des placements possibles.
        - header (list): Liste des noms de colonnes (cellules + pièces).
        """
        num_cells = self.plateau.lignes * self.plateau.colonnes
        header = ['C{}'.format(i) for i in range(num_cells)] + [p.nom for p in self.pieces.values()]

        matrix = []
        used_pieces = set(self.fixed_pieces.keys())
        pieces_non_fixees = [p for p in self.pieces.values() if p.nom not in used_pieces]
        # Tri selon l'heuristique (par défaut décroissant sur le poids)
        pieces_non_fixees.sort(key=lambda p: -self.piece_weights[p.nom])

        # Ajout des placements possibles pour les pièces non fixées
        for piece in pieces_non_fixees:
            self.add_piece_to_matrix(piece, matrix, num_cells)

        # Ajout des placements des pièces déjà fixées en tête de matrice
        for piece_name, info in self.fixed_pieces.items():
            piece = self.pieces[piece_name]
            self.add_fixed_piece_to_matrix(piece, info, matrix, num_cells)

        return matrix, header

    def add_piece_to_matrix(self, piece, matrix, num_cells):
        """
        Génère toutes les lignes de la matrice correspondant aux placements possibles d'une pièce non fixée.

        Paramètres:
        - piece (Piece): La pièce à ajouter
        - matrix (list): La matrice en cours de construction
        - num_cells (int): Nombre total de cellules du plateau (pour indexer les colonnes)

        Pour chaque variante de la pièce, on tente de la placer à chaque position possible du plateau.
        Si elle rentre sans collision et dans les limites, on crée une ligne de la matrice.
        """
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
        """
        Ajoute une pièce déjà fixée à la matrice. Cette ligne sera prioritaire et mise en tête.

        Paramètres:
        - piece (Piece): La pièce fixée
        - info (dict): Informations sur la variante et la position {'variante_index':..., 'position':...}
        - matrix (list): La matrice à mettre à jour
        - num_cells (int): Nombre total de cellules du plateau
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
        Crée une ligne de la matrice représentant un placement donné:
        - Les colonnes de cellules couvertes par la pièce sont mises à 1
        - La colonne correspondante à la pièce est mise à 1

        Paramètres:
        - piece (Piece): Pièce à placer
        - variante (np.ndarray): Variante de la pièce (matrice 2D avec 1 pour cellule occupée)
        - position (tuple): (i, j) position de placement dans le plateau
        - num_cells (int): Nombre total de cellules du plateau

        Retourne:
        - row (list): Ligne de la matrice de contraintes (liste de 0/1)
        - cells_covered (list): Liste des cellules (i,j) couvertes par ce placement
        """
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