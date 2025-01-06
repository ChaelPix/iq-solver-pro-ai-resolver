import random
from collections import deque

class GridPolyminoGenerator:
    """
    Générateur de polyominos uniques à partir d'une grille.
    Permet de diviser une grille de dimensions données en polyominos aléatoires
    tout en garantissant que toutes les cases de la grille sont remplies.
    """

    PIECE_COLORS = {
        "red": "red", "orange": "orange", "yellow": "yellow", "lime": "lime",
        "green": "green", "white": "lightblue", "cyan": "cyan", "skyblue": "skyblue",
        "blue": "blue", "purple": "purple", "darkred": "darkred", "pink": "pink",
        "gray": "gray12", "magenta": "magenta2", "gold": "gold", "coral": "coral",
        "chartreuse": "chartreuse", "darkgreen": "darkgreen", "navy": "navy", "violet": "violet",
        "tan": "tan", "salmon": "salmon", "turquoise": "turquoise", "indigo": "indigo",
        "chocolate": "chocolate", "orchid": "orchid", "plum": "plum", "slateblue": "slateblue",
        "khaki": "khaki", "seagreen": "seagreen", "goldenrod": "goldenrod", "lightcoral": "lightcoral",
        "darkorange": "darkorange", "springgreen": "springgreen", "deepskyblue": "deepskyblue",
        "dodgerblue": "dodgerblue", "mediumorchid": "mediumorchid", "firebrick": "firebrick",
        "darkslategray": "darkslategray", "sienna": "sienna", "mediumseagreen": "mediumseagreen",
        "royalblue": "royalblue", "mediumpurple": "mediumpurple", "lightsteelblue": "lightsteelblue",
        "palegreen": "palegreen", "darkmagenta": "darkmagenta"
    }

    def __init__(self, rows, cols, max_pieces=50):
        if rows < 1 or cols < 1:
            raise ValueError("Les dimensions de la grille doivent être supérieures à 1.")
        self.rows = rows
        self.cols = cols
        self.grid = [[-1 for _ in range(cols)] for _ in range(rows)]  # Grille initiale
        self.polyominos = []  # Liste des polyominos générés
        self.max_pieces = min(max_pieces, len(self.PIECE_COLORS))

    def generate(self):
        """
        Génère des polyominos uniques pour remplir toute la grille.
        """
        visited = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        label = 0

        for i in range(self.rows):
            for j in range(self.cols):
                if not visited[i][j] and label < self.max_pieces:
                    size = random.randint(2, min(self.rows, self.cols))  # Taille aléatoire
                    polyomino = self._create_polymino(i, j, size, visited, label)
                    if polyomino:
                        self.polyominos.append(polyomino)
                        label += 1

        # Remplir les cases restantes
        self._fill_remaining_cells()

    def _create_polymino(self, start_x, start_y, size, visited, label):
        """
        Crée un polyomino à partir d'une position de départ.

        Paramètres:
        - start_x (int): Ligne de départ.
        - start_y (int): Colonne de départ.
        - size (int): Taille souhaitée du polyomino.
        - visited (list): Grille des cellules visitées.
        - label (int): Étiquette du polyomino.

        Retourne:
        - list: Liste des coordonnées du polyomino ou None si impossible.
        """
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Droite, Bas, Gauche, Haut
        queue = deque([(start_x, start_y)])
        polyomino = []

        while queue and len(polyomino) < size:
            x, y = queue.popleft()
            if 0 <= x < self.rows and 0 <= y < self.cols and not visited[x][y]:
                visited[x][y] = True
                self.grid[x][y] = label
                polyomino.append((x, y))

                random.shuffle(directions)  # Mélange des directions pour ajouter de l'aléatoire
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.rows and 0 <= ny < self.cols and not visited[nx][ny]:
                        queue.append((nx, ny))

        # Si on n'a pas pu atteindre la taille souhaitée, annuler
        if len(polyomino) < size:
            for x, y in polyomino:
                visited[x][y] = False
                self.grid[x][y] = -1
            return None

        return polyomino

    def _fill_remaining_cells(self):
        """
        Remplit les cases restantes (étiquetées -1) en les assignant
        au polyomino voisin le plus petit.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == -1:  # Case non assignée
                    # Trouver les voisins valides
                    neighbors = self._get_neighbors(i, j)
                    if neighbors:
                        # Trouver le polyomino le plus petit parmi les voisins
                        neighbor_sizes = {self.grid[x][y]: len(self.polyominos[self.grid[x][y]]) for x, y in neighbors}
                        smallest_poly_label = min(neighbor_sizes, key=neighbor_sizes.get)

                        # Assigner cette case au polyomino le plus petit
                        self.grid[i][j] = smallest_poly_label
                        self.polyominos[smallest_poly_label].append((i, j))

    def _get_neighbors(self, x, y):
        """
        Trouve les voisins valides d'une case donnée.

        Paramètres:
        - x (int): Ligne de la case.
        - y (int): Colonne de la case.

        Retourne:
        - list: Liste des coordonnées des voisins ayant des labels valides.
        """
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != -1:
                neighbors.append((nx, ny))
        return neighbors

    def get_piece_definitions(self):
        """
        Retourne la liste des polyominos sous forme de `piece_definitions`.

        Retourne:
        - list: Liste de tuples (nom, forme), où `nom` est une couleur unique et `forme` est un tableau 2D.
        """
        piece_definitions = []

        for idx, polyomino in enumerate(self.polyominos):
            # Déterminer la forme (dimension minimale englobante)
            min_x = min(cell[0] for cell in polyomino)
            max_x = max(cell[0] for cell in polyomino)
            min_y = min(cell[1] for cell in polyomino)
            max_y = max(cell[1] for cell in polyomino)

            rows = max_x - min_x + 1
            cols = max_y - min_y + 1

            # Créer la forme englobante
            shape = [[0 for _ in range(cols)] for _ in range(rows)]
            for x, y in polyomino:
                shape[x - min_x][y - min_y] = 1

            # Ajouter au résultat
            color = list(self.PIECE_COLORS.keys())[idx]
            piece_definitions.append((color, shape))

        return piece_definitions

    def display_grid(self):
        """
        Affiche la grille générée avec des polyominos étiquetés.
        """
        print("Grille générée :")
        for row in self.grid:
            print(" ".join(f"{cell:2}" if cell != -1 else " ." for cell in row))


if __name__ == "__main__":
    print("Bienvenue dans le générateur de polyominos.")
    rows = int(input("Entrez le nombre de lignes: "))
    cols = int(input("Entrez le nombre de colonnes: "))
    max_pieces = int(input("Entrez le nombre maximum de pièces (50 max): "))

    generator = GridPolyminoGenerator(rows, cols, max_pieces)
    generator.generate()
    generator.display_grid()

    print("\nDéfinitions des pièces :")
    piece_definitions = generator.get_piece_definitions()
    formatted_output = "[\n"
    for name, shape in piece_definitions:
        formatted_output += f'    ("{name}", [\n'
        for row in shape:
            formatted_output += f'        {row},\n'
        formatted_output += "    ]),\n"
    formatted_output += "]"

    print(formatted_output)
