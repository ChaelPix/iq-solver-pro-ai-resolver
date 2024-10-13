import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

class Piece:
    def __init__(self, nom, forme):
        self.nom = nom
        self.forme = np.array(forme).astype(np.uint8)
        self.valeur = None
        self.variantes = self.generer_variantes()

    def generer_variantes(self):
        variantes = []
        for piece in [self.forme, np.fliplr(self.forme)]:
            for k in range(4):
                variante = np.rot90(piece, k)
                if not any(np.array_equal(variante, v) for v in variantes):
                    variantes.append(variante)
        return variantes

class Grille:
    def __init__(self, lignes=5, colonnes=11, pieces=None, couleurs=None):
        self.lignes = lignes
        self.colonnes = colonnes
        self.grille = np.zeros((lignes, colonnes), dtype=np.uint8)
        self.pieces = pieces
        self.couleurs = couleurs if couleurs is not None else ['white']

    def afficher_grille(self):
        print(self.grille)

    def sauvegarder_grille_plot(self, fichier="g.png"):
        cmap = mcolors.ListedColormap(self.couleurs)
        plt.matshow(self.grille, cmap=cmap)

        ticks_cbar = range(len(self.couleurs))
        etiquettes = ['Vide']
        for idx in range(1, len(self.couleurs)):
            for piece in self.pieces.values():
                if piece.valeur == idx:
                    etiquettes.append(piece.nom)
                    break

        cbar = plt.colorbar(ticks=ticks_cbar, boundaries=np.arange(-0.5, len(self.couleurs), 1))
        cbar.ax.set_yticklabels(etiquettes)

        plt.gcf().set_facecolor('white')
        plt.savefig(fichier, facecolor='white')
        plt.close()

    def peut_placer(self, piece, ligne, colonne):
        hauteur, largeur = piece.shape
        if ligne + hauteur > self.lignes or colonne + largeur > self.colonnes:
            return False
        region = self.grille[ligne:ligne + hauteur, colonne:colonne + largeur]
        return not np.any(region * piece)

    def placer_piece(self, piece, ligne, colonne, valeur):
        self.grille[ligne:ligne + piece.shape[0], colonne:colonne + piece.shape[1]] += (piece * valeur).astype(np.uint8)

class NiveauSelctionne:
    def __init__(self, grille, pieces, placements):
        self.grille = grille
        self.pieces = pieces
        self.placements = placements

    def placer_pieces_predefinies(self):
        for placement in self.placements:
            nom = placement['nom']
            indice_variante = placement['variante']
            position = placement['position']
            piece = self.pieces[nom]
            variante = piece.variantes[indice_variante]
            ligne, colonne = position
            if self.grille.peut_placer(variante, ligne, colonne):
                self.grille.placer_piece(variante, ligne, colonne, piece.valeur)
            else:
                print(f"piece: {nom} à la position {position} pas ok")

def definir_pieces():
    pieces = {}

    pieces['rouge'] = Piece('rouge', [
        [1, 1, 1, 1],
        [0, 0, 0, 1]
    ])

    pieces['orange'] = Piece('orange', [
        [0, 1, 0],
        [1, 1, 1],
        [1, 0, 0]
    ])

    pieces['jaune'] = Piece('jaune', [
        [1, 1, 1, 1],
        [0, 1, 0, 0]
    ])

    pieces['lime'] = Piece('lime', [
        [1, 1, 1],
        [1, 0, 1]
    ])

    pieces['vert'] = Piece('vert', [
        [1, 1, 1],
        [0, 1, 0]
    ])

    pieces['blanc'] = Piece('blanc', [
        [1, 1, 1],
        [0, 1, 1]
    ])

    pieces['cyan'] = Piece('cyan', [
        [0, 1],
        [1, 1]
    ])

    pieces['cyanbleu'] = Piece('cyanbleu', [
        [1, 1, 1],
        [1, 0, 0],
        [1, 0, 0]
    ])

    pieces['bleu'] = Piece('bleu', [
        [0, 0, 1],
        [1, 1, 1]
    ])

    pieces['violet'] = Piece('violet', [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 1]
    ])

    pieces['magenta'] = Piece('magenta', [
        [0, 1, 1],
        [1, 1, 0]
    ])

    pieces['rose'] = Piece('rose', [
        [1, 1, 0, 0],
        [0, 1, 1, 1]
    ])

    for idx, nom_piece in enumerate(pieces.keys(), start=1):
        pieces[nom_piece].valeur = idx

    return pieces

def main():
    pieces = definir_pieces()

    mapping_couleurs = {
        'vide': 'white',
        'rouge': 'red',
        'orange': 'orange',
        'jaune': 'yellow',
        'lime': 'lime',
        'vert': 'green',
        'blanc': 'lightgray',
        'cyan': 'cyan',
        'cyanbleu': 'deepskyblue',
        'bleu': 'blue',
        'violet': 'purple',
        'magenta': 'magenta',
        'rose': 'pink'
    }

    liste_couleurs = ['white']
    for idx in range(1, len(pieces) + 1):
        for piece in pieces.values():
            if piece.valeur == idx:
                liste_couleurs.append(mapping_couleurs[piece.nom])
                break

    grille = Grille(pieces=pieces, couleurs=liste_couleurs)

    placements_predefinis = [
        {'nom': 'rouge', 'variante': 3, 'position': (0, 0)},
        {'nom': 'orange', 'variante': 0, 'position': (2, 3)},
        {'nom': 'magenta', 'variante': 0, 'position': (3, 8)},
    ]

    placement = NiveauSelctionne(grille, pieces, placements_predefinis)
    placement.placer_pieces_predefinies()

    grille.afficher_grille()
    grille.sauvegarder_grille_plot("grille_puzzle_couleurs.png")

if __name__ == "__main__":
    main()
