from algorithm_stats import AlgorithmStats
from constraint_matrix_builder import ConstraintMatrixBuilder
from zone_checker import ZoneChecker
from solution_validator import SolutionValidator
from dlx_bridge import DLXBridge
import numpy as np
import os
import logging
import time

logger = logging.getLogger("algo_x_dlx")

class AlgorithmXDLX:
    """
    Implementation of Algorithm X using the optimized Dancing Links (DLX) C library.
    This version minimizes Python-C data transfers by handling most of the algorithm in C.

    Parameters:
    - plateau (Plateau): Game board
    - pieces (dict): Dictionary of pieces, {name: Piece}
    - heuristic (str): Heuristic for piece ordering
    - fixed_pieces (dict): Pre-placed pieces, optional
    - find_all_solutions (bool): Whether to find all solutions or stop at first solution
    """
    def __init__(self, plateau, pieces, heuristic="ascender", fixed_pieces=None, find_all_solutions=True):
        self.plateau = plateau
        self.pieces = pieces
        self.fixed_pieces = fixed_pieces if fixed_pieces else {}
        self.solutions = []
        self.zone_cache = {}
        self.stop_requested = False
        self.find_all_solutions = find_all_solutions
        self.piece_weights = self.calculate_piece_weights(heuristic)
        self.stats = AlgorithmStats()
        self.dlx_bridge = DLXBridge()
        
        # For mapping between row_ids and placements
        self.row_to_placement = {}
        self.current_solution_steps = []

        self.stats.reset_stats()
        self.stats.start_timer()

    def request_stop(self):
        """Request algorithm to stop"""
        self.stop_requested = True
        self.dlx_bridge.request_stop()

    def get_stats(self):
        """Return current algorithm statistics"""
        stats = self.stats.get_stats()
        
        # Update with DLX stats if available
        if hasattr(self, 'dlx_bridge'):
            dlx_stats = self.dlx_bridge.get_stats()
            stats.update({
                'branches_explored': dlx_stats['branches_explored'],
                'branches_pruned': dlx_stats['branches_pruned'],
                'placements_testes': dlx_stats['placements_tested']
            })
        
        return stats

    def get_current_solution_steps(self):
        """Return steps of the current solution"""
        return self.current_solution_steps

    def get_solutions(self):
        """Return all found solutions"""
        return self.solutions.copy()

    def calculate_piece_weights(self, heuristic="ascender"):
        """Calculate weights for pieces based on the selected heuristic"""
        # Same implementation as in the original AlgorithmX class
        weights = {}
        for piece in self.pieces.values():
            if not hasattr(piece, 'forme_base') or piece.forme_base is None:
                weights[piece.nom] = float('inf')
                continue

            occupied_cells = np.count_nonzero(piece.forme_base)
            if occupied_cells == 0:
                weights[piece.nom] = float('inf')
                continue

            shape = piece.forme_base
            height, width = shape.shape
            compactness = min(height, width) / max(height, width)
            perimeter = np.sum(np.pad(shape, pad_width=1, mode='constant', constant_values=0) != 0) - occupied_cells
            holes = np.sum(shape == 0)

            if heuristic == "ascender":
                weights[piece.nom] = 1 / occupied_cells
            elif heuristic == "descender":
                weights[piece.nom] = occupied_cells
            elif heuristic == "compactness":
                weights[piece.nom] = compactness
            elif heuristic == "compactness_inverse":
                weights[piece.nom] = 1 / (compactness + 1e-6)
            elif heuristic == "perimeter":
                weights[piece.nom] = 1 / perimeter if perimeter > 0 else float('inf')
            elif heuristic == "perimeter_inverse":
                weights[piece.nom] = perimeter
            elif heuristic == "holes":
                weights[piece.nom] = 1 / (holes + 1)
            elif heuristic == "holes_inverse":
                weights[piece.nom] = holes
            else:
                raise ValueError(f"Unknown heuristic: {heuristic}")

        return weights

    def solve(self):
        """
        Start the solving process by building the constraint matrix and 
        using the optimized DLX implementation.

        Returns:
            List of solutions
        """
        # Build constraint matrix
        builder = ConstraintMatrixBuilder(self.plateau, self.pieces, self.piece_weights, self.fixed_pieces)
        matrix, header = builder.create_constraint_matrix()
        
        # Initialize DLX solver
        num_columns = len(header)
        # Set max_solutions to 1 if we only want the first solution
        max_solutions = 1000 if self.find_all_solutions else 1
        
        if not self.dlx_bridge.create_solver(num_columns, max_solutions):
            logger.error("Failed to create DLX solver. Using Python fallback...")
            return self.solve_python_fallback(matrix, header)
            
        # Add rows to DLX solver
        logger.info(f"Building DLX matrix with {len(matrix)} rows and {num_columns} columns...")
        start_time = time.time()
        
        for row_id, row_data in enumerate(matrix):
            # Store mapping from row_id to placement data
            self.row_to_placement[row_id] = row_data
            # Add row to DLX solver
            self.dlx_bridge.add_row(row_id, row_data['row'])
            
        logger.info(f"DLX matrix built in {time.time() - start_time:.3f} seconds")
        solution_found = False
            
        # Define callback for solutions
        def solution_callback(row_ids):
            nonlocal solution_found
            solution = [self.row_to_placement[row_id] for row_id in row_ids]
            validator = SolutionValidator(self.pieces, self.plateau)
            if validator.validate_solution(solution):
                self.solutions.append(solution.copy())
                self.current_solution_steps = solution.copy()
                self.stats.add_solution(solution)
                self.stats.set_current_solution_steps(solution)
                solution_found = True
                
                # If we only want the first solution, request stop after finding one
                if not self.find_all_solutions:
                    self.request_stop()
        
        # Solve using DLX
        logger.info("Starting DLX solver...")
        start_time = time.time()
        num_solutions = self.dlx_bridge.solve(solution_callback)
        self.stats.stop_timer()
        
        if solution_found:
            logger.info(f"DLX solver completed in {time.time() - start_time:.3f} seconds, found {len(self.solutions)} solutions")
        else:
            logger.info(f"DLX solver completed in {time.time() - start_time:.3f} seconds, no solutions found")
        
        # Free DLX resources
        self.dlx_bridge.free_solver()
        
        return self.solutions

    def solve_python_fallback(self, matrix, header):
        """
        Fallback to Python implementation if DLX initialization fails.
        Uses the original algorithm_x implementation.
        """
        from algo_x_knuth import AlgorithmX
        
        logger.warning("Using Python fallback implementation")
        fallback = AlgorithmX(self.plateau, self.pieces, "ascender", self.fixed_pieces)
        solutions = fallback.solve()
        
        # Copy solutions and stats
        self.solutions = solutions
        self.stats = fallback.stats
        
        return self.solutions
