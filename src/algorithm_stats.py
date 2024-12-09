import time

class AlgorithmStats:
    """
    Classe responsable de la gestion des statistiques de l'algorithme.
    Elle permet de suivre l'évolution de l'exécution en termes de temps,
    du nombre de calculs, de placements testés, du nombre de branches explorées et coupées,
    de la profondeur de récursion, du nombre de solutions trouvées, etc.

    Paramètres:
    - Aucun paramètre particulier, la classe est autonome.

    Exemples d'utilisation:
    stats = AlgorithmStats()
    stats.increment_calculs()
    stats.get_stats() # Retourne un dictionnaire récapitulatif des statistiques
    """
    def __init__(self):
        self.reset_stats()

    def reset_stats(self):
        """
        Réinitialise toutes les statistiques pour un nouvel algorithme.
        """
        self.start_time = None  # Temps de départ (remis à None au reset).
        self.end_time = None  # Temps de fin (pour calculer la durée totale).
        self.calculs = 0  # Nombre total de calculs/itérations effectuées.
        self.placements_testes = 0  # Nombre de placements de pièces testés.
        self.solution_steps = []  # Étapes (placements) de la dernière solution trouvée.
        self.branches_explored = 0  # Nombre de branches explorées lors de l'exploration du backtracking.
        self.branches_pruned = 0  # Nombre de branches coupées (pruning) car identifiées comme sans issue.
        self.max_recursion_depth = 0  # Profondeur maximale de récursion atteinte par l'algorithme.
        self.current_recursion_depth = 0  # Profondeur actuelle de récursion.
        self.solutions_found = 0  # Nombre de solutions complètes trouvées.

    def increment_calculs(self):
        self.calculs += 1

    def increment_placements_testes(self):
        self.placements_testes += 1

    def increment_branches_explored(self):
        self.branches_explored += 1

    def increment_branches_pruned(self):
        self.branches_pruned += 1

    def update_max_depth(self):
        if self.current_recursion_depth > self.max_recursion_depth:
            self.max_recursion_depth = self.current_recursion_depth

    def increment_depth(self):
        """
        Incrémente la profondeur courante de récursion et met à jour la profondeur max si besoin.
        """
        self.current_recursion_depth += 1
        self.update_max_depth()

    def decrement_depth(self):
        """
        Décrémente la profondeur courante de récursion après le retour d'un appel récursif.
        """
        self.current_recursion_depth -= 1

    def add_solution(self, solution):
        """
        Ajoute une solution trouvée et met à jour les compteurs.

        Paramètres:
        - solution (list): Liste des placements qui constituent la solution trouvée.
        """
        self.solution_steps = solution.copy()
        self.solutions_found += 1

    def start_timer(self):
        """
        Démarre le chronomètre pour mesurer la durée de l'algorithme.
        """
        self.start_time = time.time()
        self.end_time = None

    def stop_timer(self):
        """
        Arrête le chronomètre et enregistre le temps final.
        """
        if self.start_time is not None:
            self.end_time = time.time()

    def get_time_elapsed(self):
        """
        Retourne le temps écoulé depuis le début de l'algorithme.
        Si l'algorithme est terminé, retourne la durée totale.
        """
        if self.start_time is None:
            return 0
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def get_stats(self):
        """
        Retourne un dictionnaire des statistiques actuelles de l'algorithme.
        Utile pour un affichage ou pour une analyse post-traitement.

        Retourne:
        - dict: contenant 'time', 'calculs', 'placements_testes', 'branches_explored',
                'branches_pruned', 'max_recursion_depth', 'solutions_found'
        """
        return {
            "time": self.get_time_elapsed(),
            "calculs": self.calculs,
            "placements_testes": self.placements_testes,
            "branches_explored": self.branches_explored,
            "branches_pruned": self.branches_pruned,
            "max_recursion_depth": self.max_recursion_depth,
            "solutions_found": self.solutions_found
        }

    def get_current_solution_steps(self):
        """
        Retourne une copie des étapes de la dernière solution trouvée.
        Chaque étape correspond à un placement d'une pièce sur le plateau.
        """
        return self.solution_steps.copy()