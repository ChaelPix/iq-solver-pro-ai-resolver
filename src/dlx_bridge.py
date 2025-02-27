import os
import ctypes
import logging
from typing import List, Callable, Dict, Any, Tuple, Optional

logger = logging.getLogger("dlx_bridge")

# Callback function type for solution reporting
SOLUTION_CALLBACK = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.c_int)

class DLXBridge:
    """
    Bridge to the C implementation of the Dancing Links (DLX) algorithm.
    This provides a Pythonic interface to the C-based DLX solver.
    """
    def __init__(self):
        self.dlx_lib = None
        self.dlx_solver = None
        self._matrix_rows = []  # Keep references to Python objects
        self._row_data_ptrs = []  # Keep references to C pointers
        self._load_library()
    
    def _load_library(self):
        """Load the C library for DLX"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            lib_path = os.path.join(current_dir, 'dlx_solver.so')
            
            if not os.path.exists(lib_path):
                logger.warning(f"DLX library not found at {lib_path}. Compilation required.")
                return
                
            self.dlx_lib = ctypes.CDLL(lib_path)
            
            # Define function prototypes
            self.dlx_lib.dlx_create.argtypes = [ctypes.c_int, ctypes.c_int]
            self.dlx_lib.dlx_create.restype = ctypes.c_void_p
            
            self.dlx_lib.dlx_add_row.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
            self.dlx_lib.dlx_add_row.restype = None
            
            self.dlx_lib.dlx_solve.argtypes = [ctypes.c_void_p, SOLUTION_CALLBACK]
            self.dlx_lib.dlx_solve.restype = ctypes.c_int
            
            self.dlx_lib.dlx_free.argtypes = [ctypes.c_void_p]
            self.dlx_lib.dlx_free.restype = None
            
            self.dlx_lib.dlx_stop.argtypes = [ctypes.c_void_p]
            self.dlx_lib.dlx_stop.restype = None
            
            self.dlx_lib.dlx_get_stats.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
            self.dlx_lib.dlx_get_stats.restype = None
            
            logger.info("Successfully loaded DLX library")
            
        except Exception as e:
            logger.error(f"Failed to load DLX library: {e}")
            self.dlx_lib = None
    
    def create_solver(self, num_columns: int, max_solutions: int = 1000) -> bool:
        """
        Initialize a new DLX solver
        
        Args:
            num_columns: Number of columns in the constraint matrix
            max_solutions: Maximum number of solutions to find
            
        Returns:
            True if initialization succeeded, False otherwise
        """
        if self.dlx_lib is None:
            logger.error("DLX library not loaded")
            return False
            
        if self.dlx_solver:
            self.free_solver()
            
        self.dlx_solver = self.dlx_lib.dlx_create(num_columns, max_solutions)
        self._matrix_rows = []
        self._row_data_ptrs = []
        
        return self.dlx_solver is not None
    
    def add_row(self, row_id: int, row_data: List[int]) -> bool:
        """
        Add a row to the constraint matrix
        
        Args:
            row_id: ID of the row, will be returned in solutions
            row_data: List of 0s and 1s representing the row
            
        Returns:
            True if the row was added successfully
        """
        if not self.dlx_solver:
            logger.error("DLX solver not initialized")
            return False
            
        # Convert row data to C array
        c_row_data = (ctypes.c_int * len(row_data))(*row_data)
        self._matrix_rows.append(row_data)  # Keep a reference
        self._row_data_ptrs.append(c_row_data)  # Keep a reference
        
        self.dlx_lib.dlx_add_row(self.dlx_solver, row_id, c_row_data)
        return True
    
    def solve(self, solution_callback: Callable[[List[int]], None]) -> int:
        """
        Solve the constraint matrix
        
        Args:
            solution_callback: Function to call when a solution is found,
                              receives a list of row IDs as parameter
                              
        Returns:
            Number of solutions found
        """
        if not self.dlx_solver:
            logger.error("DLX solver not initialized")
            return 0
        
        # Define a callback function that will be called from C
        def solution_handler(solution_ptr, count):
            if solution_ptr and count > 0:
                # Convert C array to Python list
                solution = [solution_ptr[i] for i in range(count)]
                solution_callback(solution)
        
        # Convert to a C-compatible function pointer
        c_callback = SOLUTION_CALLBACK(solution_handler)
        
        # Call the C solver
        return self.dlx_lib.dlx_solve(self.dlx_solver, c_callback)
    
    def request_stop(self) -> None:
        """Request the solver to stop early"""
        if self.dlx_solver:
            self.dlx_lib.dlx_stop(self.dlx_solver)
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics from the solver
        
        Returns:
            Dictionary with statistics:
            - branches_explored: Number of branches explored
            - branches_pruned: Number of branches pruned
            - placements_tested: Number of placements tested
            - solutions_found: Number of solutions found
        """
        if not self.dlx_solver:
            return {
                'branches_explored': 0,
                'branches_pruned': 0,
                'placements_tested': 0,
                'solutions_found': 0
            }
        
        stats = (ctypes.c_int * 4)()
        self.dlx_lib.dlx_get_stats(self.dlx_solver, stats)
        
        return {
            'branches_explored': stats[0],
            'branches_pruned': stats[1],
            'placements_tested': stats[2],
            'solutions_found': stats[3]
        }
    
    def free_solver(self) -> None:
        """Free resources used by the solver"""
        if self.dlx_solver:
            self.dlx_lib.dlx_free(self.dlx_solver)
            self.dlx_solver = None
            self._matrix_rows = []
            self._row_data_ptrs = []
    
    def __del__(self):
        """Clean up resources on destruction"""
        self.free_solver()
