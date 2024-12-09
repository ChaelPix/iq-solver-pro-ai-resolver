from algo_x_knuth import AlgorithmX

class SolverManager:
    """
    Classe intermédiaire pour gérer la résolution du puzzle.
    Elle encapsule l'algorithme X et fournit des méthodes pour:
    - Lancer la résolution.
    - Vérifier si l'algorithme est toujours en cours.
    - Récupérer les statistiques et la solution en cours.
    - Arrêter l'algorithme au besoin.

    L'idée est que l'interface puisse appeler périodiquement get_stats() et get_current_solution(),
    tant que is_running() est True, afin d'afficher le progrès. Une fois terminé, on peut afficher
    la solution finale.

    Paramètres:
    - plateau (Plateau): Copie du plateau initial.
    - pieces (dict): Dictionnaire des pièces {nom: Piece}.
    - heuristic_ascender (bool): Heuristique pour l'ordre des pièces.
    - fixed_pieces (dict): Pièces pré-placées, optionnel.

    Utilisation:
    manager = SolverManager(plateau_copy, pieces, heuristic_ascender, fixed_pieces)
    manager.run()
    while manager.is_running():
        stats = manager.get_stats()
        current_sol = manager.get_current_solution_steps()
        # Mettre à jour l'affichage
    final_solutions = manager.get_solutions()
    """
    def __init__(self, plateau, pieces, heuristic_choice, fixed_pieces=None):
        self.plateau = plateau
        self.pieces = pieces
        self.heuristic = heuristic_choice
        self.fixed_pieces = fixed_pieces if fixed_pieces else {}
        self.algo = None
        self.running = False

    def run(self):
        """
        Lance l'algorithme de résolution.
        Cette méthode exécute l'algorithme X, ce qui peut prendre du temps.
        On peut imaginer la lancer dans un thread séparé pour ne pas bloquer l'UI,
        mais ici on la lance directement. L'interface peut régulièrement
        consulter get_stats() et get_current_solution_steps() pour suivre la progression.
        """
        self.algo = AlgorithmX(
            self.plateau,
            self.pieces,
            self.heuristic,
            self.fixed_pieces
        )
        self.running = True
        self.algo.solve()
        self.running = False

    def is_running(self):
        """
        Indique si l'algorithme est toujours en cours.
        Retourne:
        - bool: True si encore en train de chercher, False sinon.
        """
        return self.running and not self.algo.stop_requested

    def request_stop(self):
        """
        Demande l'arrêt prématuré de l'algorithme.
        """
        if self.algo:
            self.algo.request_stop()
            self.running = False

    def get_stats(self):
        """
        Récupère les statistiques courantes de l'algorithme.
        Même si l'algo est fini, on peut obtenir les stats finales.

        Retourne:
        - dict: Dictionnaire contenant le temps, calculs, placements_testes, branches_explored, etc.
        """
        if self.algo:
            return self.algo.get_stats()
        return {}

    def get_current_solution_steps(self):
        """
        Récupère la liste des placements choisis jusqu'à présent (solution partielle).

        Retourne:
        - list: Liste des étapes (chacune contenant 'piece', 'cells_covered', etc.)
        """
        if self.algo:
            return self.algo.get_current_solution_steps()
        return []

    def get_solutions(self):
        """
        Retourne toutes les solutions trouvées. Généralement après la fin de l'algo.

        Retourne:
        - list: Liste de solutions complètes.
        """
        if self.algo:
            return self.algo.get_solutions()
        return []
