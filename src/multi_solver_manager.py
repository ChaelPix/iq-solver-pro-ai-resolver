import threading
import time
from solve_manager import SolverManager

class MultiHeuristicManager:
    """
    Cette classe lance plusieurs SolverManager en parallèle, chacun avec une heuristique différente.
    Elle attend que la première solution arrive (ou qu'un manager termine),
    puis arrête tous les autres et retourne la solution et les stats du premier fini.

    Paramètres:
    - plateau (Plateau): Copie du plateau initial.
    - pieces (dict): Dictionnaire des pièces {nom: Piece}.
    - heuristics (list): Liste des heuristiques à lancer en parallèle. Ex: ["ascender", "descender", "holes"]
    - fixed_pieces (dict): Pièces pré-placées, optionnel.

    Utilisation:
    multi_manager = MultiHeuristicManager(plateau_copy, pieces, ["ascender", "descender", "holes"], fixed_pieces)
    multi_manager.run_all()
    # On peut ensuite périodiquement checker:
    # finished, stats, solution = multi_manager.check_status()
    # finished = True si l'une des branches a terminé. On récupère stats et solution.
    """

    def __init__(self, plateau, pieces, heuristics, fixed_pieces=None):
        self.plateau = plateau
        self.pieces = pieces
        self.heuristics = heuristics
        self.fixed_pieces = fixed_pieces if fixed_pieces else {}
        
        self.managers = []
        self.threads = []
        self.results = {}
        self.lock = threading.Lock()
        # results aura la structure {heuristic_name: {"finished": bool, "stats": {}, "solution": [], "running": bool}}

        for h in self.heuristics:
            mgr = SolverManager(self.plateau, self.pieces, h, self.fixed_pieces)
            self.managers.append((h, mgr))
            self.results[h] = {
                "finished": False,
                "stats": {},
                "solution": [],
                "running": False
            }

    def run_all(self):
        """
        Lance tous les SolverManager dans des threads séparés.
        """
        for h, mgr in self.managers:
            t = threading.Thread(target=self._run_manager, args=(h, mgr), daemon=True)
            self.threads.append(t)
            self.results[h]["running"] = True
            t.start()

    def _run_manager(self, heuristic, mgr):
        """
        Méthode interne appelée par chaque thread pour exécuter le SolverManager.
        On attend la fin de la résolution, puis on enregistre les résultats.
        """
        mgr.run()  # Lance l'algo (bloquant)
        with self.lock:
            # Récupérer les stats et solutions
            stats = mgr.get_stats()
            solutions = mgr.get_solutions()
            sol = solutions[0] if solutions else []
            self.results[heuristic]["finished"] = True
            self.results[heuristic]["running"] = False
            self.results[heuristic]["stats"] = stats
            self.results[heuristic]["solution"] = sol

    def check_status(self):
        """
        Vérifie si l'une des branches a terminé.
        Retourne:
        - finished (bool): True si au moins une heuristique est finie.
        - stats (dict): Stats de la première heuristique qui a terminé.
        - solution (list): Solution de la première heuristique qui a terminé.
        - winner_heuristic (str): le nom de l'heuristique gagnante, ou "" si aucune
        Si aucune n'a terminé, retourne (False, {}, []).
        
        Une fois qu'une solution est trouvée, on arrête les autres.
        """
        with self.lock:
            for h in self.heuristics:
                if self.results[h]["finished"]:
                    self._stop_others(h)
                    return True, self.results[h]["stats"], self.results[h]["solution"], h
        return False, {}, [], ""

    def _stop_others(self, winner_heuristic):
        """
        Arrête tous les SolverManager sauf celui qui a gagné.
        """
        for h, mgr in self.managers:
            if h != winner_heuristic and self.results[h]["running"]:
                mgr.request_stop()
                self.results[h]["running"] = False

    def all_finished_or_stopped(self):
        """
        Vérifie si tous les managers sont finis ou arrêtés.
        Utile pour savoir si on peut stopper la boucle de monitoring.
        """
        with self.lock:
            return all((not r["running"]) for r in self.results.values())

    def request_stop_all(self):
        """
        Demande l'arrêt de tous les managers.
        """
        with self.lock:
            for h, mgr in self.managers:
                if self.results[h]["running"]:
                    mgr.request_stop()
                    self.results[h]["running"] = False
