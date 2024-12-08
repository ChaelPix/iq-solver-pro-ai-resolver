import numpy as np

class ZoneChecker:
    """
    Classe pour vérifier les zones vides restantes sur le plateau pendant la recherche.
    L'objectif est de détecter les situations où les zones vides ne peuvent plus être remplies
    par les pièces restantes, permettant ainsi un pruning (coupure) précoce.

    Paramètres:
    - plateau: Objet plateau (dimensions + grille)
    - pieces (dict): Dictionnaire des pièces disponibles
    - zone_cache (dict): Cache pour mémoriser la faisabilité du remplissage de zones de tailles données
    """
    def __init__(self, plateau, pieces, zone_cache):
        self.plateau = plateau
        self.pieces = pieces
        self.zone_cache = zone_cache

    def has_unfillable_voids(self, solution):
        """
        Détermine s'il existe des zones vides impossibles à remplir avec les pièces restantes.
        Pour cela:
        1. On applique la solution courante au plateau pour marquer les cellules occupées.
        2. On identifie les zones vides (suite de cellules contiguës).
        3. On vérifie si leur taille peut être atteinte par une combinaison des tailles de pièces restantes.

        Paramètres:
        - solution (list): Liste des placements actuels dans la branche de recherche.

        Retourne:
        - bool: True si une zone est impossible à remplir, False sinon.
        """
        plateau_temp = self.apply_solution_to_plateau(solution)
        empty_zones = self.get_empty_zones(plateau_temp)
        remaining_pieces = set(self.pieces.keys()) - set(sol['piece'].nom for sol in solution)
        remaining_sizes = [np.count_nonzero(self.pieces[p].forme_base) for p in remaining_pieces]

        for zone in empty_zones:
            zone_size = len(zone)
            # Vérification via le cache
            if zone_size in self.zone_cache:
                if not self.zone_cache[zone_size]:
                    return True
                else:
                    continue

            # Calcul si zone comblable
            possible = self.is_zone_fillable(zone_size, remaining_sizes)
            self.zone_cache[zone_size] = possible
            if not possible:
                return True
        return False

    def apply_solution_to_plateau(self, solution):
        """
        Applique la solution courante au plateau, retournant un plateau temporaire
        avec les placements déjà effectués.

        Paramètres:
        - solution (list): Liste des placements déjà choisis.

        Retourne:
        - plateau_temp (np.ndarray): Copie du plateau avec les pièces placées.
        """
        plateau_temp = np.copy(self.plateau.plateau)
        for sol in solution:
            for cell in sol['cells_covered']:
                i, j = cell
                plateau_temp[i, j] = 1
        return plateau_temp

    def get_empty_zones(self, plateau_temp):
        """
        Identifie toutes les zones vides dans le plateau temporaire.
        Une zone vide est un ensemble de cellules contiguës (en 4-directions) non occupées.

        Paramètres:
        - plateau_temp (np.ndarray): Plateau actuel avec placements déjà effectués.

        Retourne:
        - empty_zones (list): Liste de zones, chaque zone est une liste de coordonnées (i,j).
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
        Explore une zone vide à partir d'une cellule donnée (i,j).
        Effectue un parcours en largeur (BFS) pour récupérer toutes les cellules contiguës vides.

        Paramètres:
        - plateau_temp (np.ndarray): Plateau temporaire.
        - i (int), j (int): Coordonnées de départ pour explorer la zone.
        - visited (set): Ensemble des cellules déjà visitées.

        Retourne:
        - zone (list): Liste des cellules (i,j) constituant la zone vide explorée.
        """
        queue = [(i, j)]
        visited.add((i, j))
        zone = [(i, j)]
        while queue:
            ci, cj = queue.pop(0)
            for ni, nj in [(ci+1, cj), (ci-1, cj), (ci, cj+1), (ci, cj-1)]:
                if 0 <= ni < self.plateau.lignes and 0 <= nj < self.plateau.colonnes:
                    if plateau_temp[ni, nj] == 0 and (ni, nj) not in visited:
                        visited.add((ni, nj))
                        queue.append((ni, nj))
                        zone.append((ni, nj))
        return zone

    def is_zone_fillable(self, zone_size, remaining_sizes):
        """
        Vérifie si la taille de zone (zone_size) peut être comblée par une combinaison des pièces restantes
        dont les tailles sont dans remaining_sizes.

        Paramètres:
        - zone_size (int): Taille de la zone vide
        - remaining_sizes (list): Liste des tailles (nombre de cellules) des pièces restantes

        Retourne:
        - bool: True si on peut trouver une combinaison de pièces pour atteindre exactement zone_size.
        """
        return self.can_fill_zone(zone_size, remaining_sizes)

    def can_fill_zone(self, zone_size, piece_sizes):
        """
        Utilise une approche de type "subset sum" (programmation dynamique) pour déterminer
        si une somme de certains éléments de piece_sizes peut atteindre exactement zone_size.

        Paramètres:
        - zone_size (int): Taille cible de la zone
        - piece_sizes (list): Tailles disponibles des pièces restantes

        Retourne:
        - bool: True si une combinaison possible, False sinon.
        """
        dp = [False] * (zone_size + 1)
        dp[0] = True
        for size in piece_sizes:
            for i in range(zone_size, size - 1, -1):
                dp[i] = dp[i] or dp[i - size]
        return dp[zone_size]

