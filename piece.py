import numpy as np

class Piece:
    def __init__(self, nom, forme_base):
        self.nom = nom
        self.forme_base = np.array(forme_base)
        self.variantes = self.generer_variantes()

    def generer_variantes(self):
        variantes = []
        for i in range(4):  # (0°, 90°, 180°, 270°)
            rotation = np.rot90(self.forme_base, i)
            variantes.append(rotation)
            # symétrie horizontale
            symetrie = np.fliplr(rotation)
            variantes.append(symetrie)

        # temp, doublons
        variantes_uniques = []
        for var in variantes:
            if not any(np.array_equal(var, existante) for existante in variantes_uniques):
                variantes_uniques.append(var)
        return variantes_uniques

    def afficher_variantes(self):
        for i, variante in enumerate(self.variantes):
            print(f"Variante {i+1} de la pièce {self.nom}:")
            print(variante)
            print()
