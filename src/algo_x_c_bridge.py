import ctypes
import numpy as np
import os
import logging
import time
from algo_x_profiler import profile_function, performance_metrics, reset_performance_metrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("algo_x_c_bridge")

# Load C library
def load_algo_x_c_lib():
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the compiled C library
        lib_path = os.path.join(current_dir, 'algo_x_knuth_c.so')
        
        # Check if library exists
        if not os.path.exists(lib_path):
            logger.warning(f"C library not found at {lib_path}. Will use Python fallback.")
            return None
        
        # Load the library
        lib = ctypes.CDLL(lib_path)
        
        # Define function signatures
        lib.select_min_column.argtypes = [
            ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),  # rows_data
            ctypes.c_int,  # num_rows
            ctypes.c_int  # num_cols
        ]
        lib.select_min_column.restype = ctypes.c_int
        
        lib.cover_columns.argtypes = [
            ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),  # rows_data
            ctypes.c_int,  # num_rows
            ctypes.c_int,  # num_cols
            ctypes.POINTER(ctypes.c_int),  # columns_to_remove
            ctypes.c_int,  # num_columns_to_remove
            ctypes.c_int,  # selected_row_idx
            ctypes.POINTER(ctypes.c_int)  # result_indices
        ]
        lib.cover_columns.restype = ctypes.c_int
        
        logger.info("Successfully loaded C library for algorithm acceleration")
        return lib
    except Exception as e:
        logger.error(f"Error loading C library: {e}")
        return None

# Global library reference and cached data structures
_c_lib = None
_matrix_cache = {
    'matrix': None,
    'c_rows': None,
    'row_arrays': None,
    'num_rows': 0,
    'num_cols': 0
}

def get_c_lib():
    """Lazy-load the C library"""
    global _c_lib
    if _c_lib is None:
        _c_lib = load_algo_x_c_lib()
    return _c_lib

# Python fallback implementations with profiling
@profile_function("select_min_column_py")
def select_min_column_py(matrix, header):
    """Python implementation of select_min_column as fallback"""
    counts = [0] * len(header)
    for row in matrix:
        for idx, val in enumerate(row['row']):
            if val == 1:
                counts[idx] += 1
    counts = [c if c > 0 else float('inf') for c in counts]
    m = min(counts)
    if m == float('inf'):
        return None
    return counts.index(m)

@profile_function("cover_columns_py")
def cover_columns_py(matrix, columns_to_remove, selected_row):
    """Python implementation of cover_columns as fallback"""
    new_matrix = []
    for r in matrix:
        if r == selected_row:
            continue
        if all(r['row'][idx] == 0 for idx in columns_to_remove):
            new_matrix.append(r)
    return new_matrix

def prepare_matrix_for_c(matrix, num_cols):
    """
    Prepare the matrix data for C functions and cache it for reuse
    Returns c_rows pointer and keeps references in the cache
    """
    global _matrix_cache
    
    # If matrix hasn't changed, reuse cached data
    if (_matrix_cache['matrix'] is matrix and 
        _matrix_cache['num_cols'] == num_cols and
        _matrix_cache['num_rows'] == len(matrix)):
        return _matrix_cache['c_rows']
        
    # Create new C data structures
    num_rows = len(matrix)
    row_arrays = []
    c_rows = (ctypes.POINTER(ctypes.c_int) * num_rows)()
    
    conversion_start = time.time()
    for i, row_dict in enumerate(matrix):
        row_data = row_dict['row']
        row_arr = (ctypes.c_int * num_cols)(*row_data)
        row_arrays.append(row_arr)  # Keep reference to prevent garbage collection
        c_rows[i] = row_arr
    conversion_time = time.time() - conversion_start
    
    # Update cache with new data
    _matrix_cache['matrix'] = matrix
    _matrix_cache['c_rows'] = c_rows
    _matrix_cache['row_arrays'] = row_arrays
    _matrix_cache['num_rows'] = num_rows
    _matrix_cache['num_cols'] = num_cols
    
    # Track conversion overhead for profiling
    if 'select_min_column_c' in performance_metrics:
        performance_metrics['select_min_column_c']['overhead'] += conversion_time / 2
    if 'cover_columns_c' in performance_metrics:
        performance_metrics['cover_columns_c']['overhead'] += conversion_time / 2
    
    return c_rows

@profile_function("select_min_column_c")
def select_min_column_c(matrix, header):
    """
    C-accelerated version of select_min_column with Python fallback
    
    Args:
        matrix: List of dictionaries, each with a 'row' key containing a list of 0s and 1s
        header: List of column headers
        
    Returns:
        int: Index of the column with minimum number of 1s, or None if no valid column
    """
    c_lib = get_c_lib()
    if c_lib is None:
        logger.debug("Using Python fallback for select_min_column")
        return select_min_column_py(matrix, header)
    
    try:
        if not matrix or not header:
            return None
            
        num_rows = len(matrix)
        num_cols = len(header)
        
        # Use optimized matrix preparation
        c_rows = prepare_matrix_for_c(matrix, num_cols)
        
        # Call C function
        result = c_lib.select_min_column(c_rows, num_rows, num_cols)
        
        # Convert result
        if result == -1:
            return None
        return result
    except Exception as e:
        logger.error(f"C select_min_column failed: {e}, falling back to Python implementation")
        return select_min_column_py(matrix, header)

@profile_function("cover_columns_c")
def cover_columns_c(matrix, columns_to_remove, selected_row):
    """
    C-accelerated version of cover_columns with Python fallback
    
    Args:
        matrix: List of dictionaries, each with a 'row' key
        columns_to_remove: List of column indices to check
        selected_row: The selected row dictionary to remove
        
    Returns:
        list: New matrix with filtered rows
    """
    c_lib = get_c_lib()
    if c_lib is None:
        logger.debug("Using Python fallback for cover_columns")
        return cover_columns_py(matrix, columns_to_remove, selected_row)
    
    try:
        if not matrix:
            return []
            
        num_rows = len(matrix)
        if num_rows == 0:
            return []
            
        num_cols = len(matrix[0]['row'])
        selected_row_idx = matrix.index(selected_row)
        
        # Use optimized matrix preparation
        c_rows = prepare_matrix_for_c(matrix, num_cols)
        
        # Set up output array and other parameters
        c_columns = (ctypes.c_int * len(columns_to_remove))(*columns_to_remove)
        c_result_indices = (ctypes.c_int * num_rows)()
        
        # Call C function
        result_count = c_lib.cover_columns(
            c_rows, num_rows, num_cols, 
            c_columns, len(columns_to_remove),
            selected_row_idx, c_result_indices
        )
        
        # Build result matrix from indices
        new_matrix = []
        for i in range(result_count):
            row_idx = c_result_indices[i]
            new_matrix.append(matrix[row_idx])
        
        # After making a new matrix, invalidate the cache
        _matrix_cache['matrix'] = None
            
        return new_matrix
    except Exception as e:
        logger.error(f"C cover_columns failed: {e}, falling back to Python implementation")
        return cover_columns_py(matrix, columns_to_remove, selected_row)

# Force using Python implementation for benchmarking
def use_python_implementation():
    """Force use of Python implementation for comparative benchmarking"""
    reset_performance_metrics()
    global _c_lib
    _c_lib = None
    logger.info("Switched to Python implementation for benchmarking")

# Force using C implementation for benchmarking
def use_c_implementation():
    """Force use of C implementation for comparative benchmarking"""
    reset_performance_metrics()
    global _c_lib
    _c_lib = get_c_lib()
    logger.info("Switched to C implementation for benchmarking")

# Output final performance report at exit
import atexit
from algo_x_profiler import print_performance_report
atexit.register(print_performance_report)
