import numpy as np

class Plateau:
    def __init__(self, lignes=5, colonnes=11):
        self.plateau = np.zeros((lignes, colonnes), dtype=int)

    def afficher(self):
        print("Plateau actuel :")
        print(self.plateau)

    def placer_piece(self, piece, variante_index, position):
        variante = piece.variantes[variante_index]
        ligne, colonne = position

        if not self.peut_placer(variante, position):
            print(f"Impossible de placer la pièce {piece.nom} à la position {position}")
            return False

        for i in range(variante.shape[0]):
            for j in range(variante.shape[1]):
                if variante[i, j] == 1:
                    self.plateau[ligne + i, colonne + j] = 1
        print(f"Pièce {piece.nom} placée à la position {position} avec la variante {variante_index + 1}")
        return True

    def retirer_piece(self, piece, variante_index, position):
        variante = piece.variantes[variante_index]
        ligne, colonne = position
        for i in range(variante.shape[0]):
            for j in range(variante.shape[1]):
                if variante[i, j] == 1:
                    self.plateau[ligne + i, colonne + j] = 0

    def peut_placer(self, variante, position):
        ligne, colonne = position
        if ligne + variante.shape[0] > self.plateau.shape[0] or colonne + variante.shape[1] > self.plateau.shape[1]:
            return False

        for i in range(variante.shape[0]):
            for j in range(variante.shape[1]):
                if variante[i, j] == 1 and self.plateau[ligne + i, colonne + j] != 0:
                    return False

        return True
