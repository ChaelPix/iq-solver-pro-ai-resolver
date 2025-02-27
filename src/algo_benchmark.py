#!/usr/bin/env python3
import time
import numpy as np
import random
import logging
import argparse
from algo_x_c_bridge import select_min_column_c, cover_columns_c
from algo_x_c_bridge import select_min_column_py, cover_columns_py
from algo_x_profiler import reset_performance_metrics, print_performance_report
from constraint_matrix_builder import ConstraintMatrixBuilder
from plateau import Plateau
from piece import Piece
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("algo_benchmark")

def generate_test_matrix(num_rows, num_cols, density=0.1):
    """Generate a random test matrix with given density of 1s"""
    matrix = []
    for i in range(num_rows):
        row_data = [1 if random.random() < density else 0 for _ in range(num_cols)]
        # Ensure each row has at least one 1
        if sum(row_data) == 0:
            row_data[random.randint(0, num_cols-1)] = 1
        matrix.append({'row': row_data, 'id': i})
    
    return matrix, [f'col_{i}' for i in range(num_cols)]

def benchmark_select_min_column(matrix, header, repeats=10):
    """Benchmark both Python and C implementations of select_min_column"""
    logger.info(f"Benchmarking select_min_column with matrix size {len(matrix)}x{len(header)}")
    
    # Warm-up
    select_min_column_py(matrix, header)
    select_min_column_c(matrix, header)
    
    # Python implementation
    py_start = time.time()
    for _ in range(repeats):
        select_min_column_py(matrix, header)
    py_time = time.time() - py_start
    
    # C implementation
    c_start = time.time()
    for _ in range(repeats):
        select_min_column_c(matrix, header)
    c_time = time.time() - c_start
    
    speedup = py_time / c_time if c_time > 0 else 0
    
    logger.info(f"Python: {py_time:.4f}s, C: {c_time:.4f}s, Speedup: {speedup:.2f}x")
    return py_time, c_time, speedup

def benchmark_cover_columns(matrix, repeats=5):
    """Benchmark both Python and C implementations of cover_columns"""
    num_cols = len(matrix[0]['row'])
    logger.info(f"Benchmarking cover_columns with matrix size {len(matrix)}x{num_cols}")
    
    # Create a set of test cases to ensure both implementations handle the same inputs
    test_cases = []
    for _ in range(repeats):
        selected_row = random.choice(matrix)
        columns_to_remove = [i for i, val in enumerate(selected_row['row']) if val == 1]
        # Ensure we don't try to remove all columns
        if len(columns_to_remove) > num_cols // 2:
            columns_to_remove = columns_to_remove[:num_cols//2]
        test_cases.append((columns_to_remove, selected_row))
    
    # Python implementation
    py_start = time.time()
    py_results = []
    for columns_to_remove, selected_row in test_cases:
        py_results.append(cover_columns_py(matrix, columns_to_remove, selected_row))
    py_time = time.time() - py_start
    
    # C implementation
    c_start = time.time()
    c_results = []
    for columns_to_remove, selected_row in test_cases:
        c_results.append(cover_columns_c(matrix, columns_to_remove, selected_row))
    c_time = time.time() - c_start
    
    # Verify results are equivalent
    results_match = all(len(py_res) == len(c_res) for py_res, c_res in zip(py_results, c_results))
    
    speedup = py_time / c_time if c_time > 0 else 0
    
    logger.info(f"Python: {py_time:.4f}s, C: {c_time:.4f}s, Speedup: {speedup:.2f}x")
    if not results_match:
        logger.warning("Results between Python and C implementations don't match in size!")
        
    return py_time, c_time, speedup

def benchmark_with_real_puzzle(puzzle_size='small'):
    """Benchmark using a realistic puzzle matrix from the constraint builder"""
    logger.info(f"Benchmarking with {puzzle_size} puzzle...")
    
    if puzzle_size == 'small':
        # Small 5x5 puzzle
        plateau = Plateau(5, 5)
        num_pieces = 5
    elif puzzle_size == 'medium':
        # Medium 5x10 puzzle
        plateau = Plateau(5, 10)
        num_pieces = 10
    else:
        # Large puzzle
        plateau = Plateau(8, 12)
        num_pieces = 20
    
    # Create some test pieces
    pieces = {}
    colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'cyan', 
              'magenta', 'brown', 'pink', 'lime', 'navy', 'teal', 'olive', 
              'maroon', 'silver', 'gold', 'coral', 'violet', 'turquoise']
    
    for i in range(num_pieces):
        shape_height = random.randint(1, 3)
        shape_width = random.randint(1, 3)
        shape = [[1 if random.random() < 0.7 else 0 for _ in range(shape_width)] 
                 for _ in range(shape_height)]
        # Ensure at least one cell is 1
        if sum(sum(row) for row in shape) == 0:
            shape[0][0] = 1
        
        piece = Piece(colors[i], shape)
        pieces[colors[i]] = piece
    
    # Generate constraint matrix
    builder = ConstraintMatrixBuilder(plateau, pieces, 
                                     {p.nom: 1.0 for p in pieces.values()}, 
                                     {})
    matrix, header = builder.create_constraint_matrix()
    
    logger.info(f"Created constraint matrix of size {len(matrix)}x{len(header)}")
    
    # Benchmark both functions
    min_col_stats = benchmark_select_min_column(matrix, header, repeats=5)
    cover_cols_stats = benchmark_cover_columns(matrix, repeats=3)
    
    return min_col_stats, cover_cols_stats

def benchmark_scaling():
    """Benchmark how performance scales with matrix size"""
    sizes = [
        (100, 50),    # Small
        (500, 100),   # Medium
        (1000, 200),  # Large
        (5000, 500)   # Extra Large (if you have enough memory)
    ]
    
    results = []
    for rows, cols in sizes:
        try:
            reset_performance_metrics()
            matrix, header = generate_test_matrix(rows, cols)
            
            # Benchmark select_min_column
            min_col_stats = benchmark_select_min_column(matrix, header, repeats=3)
            
            # Benchmark cover_columns
            cover_cols_stats = benchmark_cover_columns(matrix, repeats=2)
            
            results.append({
                'size': (rows, cols),
                'min_col': min_col_stats,
                'cover_cols': cover_cols_stats
            })
        except Exception as e:
            logger.error(f"Error benchmarking size {rows}x{cols}: {e}")
    
    # Create visualization of scaling results
    plot_scaling_results(results)
    return results

def plot_scaling_results(results):
    """Plot speedup vs matrix size"""
    sizes = [f"{r}x{c}" for r, c in [res['size'] for res in results]]
    min_col_speedups = [res['min_col'][2] for res in results]
    cover_cols_speedups = [res['cover_cols'][2] for res in results]
    
    plt.figure(figsize=(10, 6))
    plt.bar(np.arange(len(sizes)) - 0.2, min_col_speedups, width=0.4, label='select_min_column')
    plt.bar(np.arange(len(sizes)) + 0.2, cover_cols_speedups, width=0.4, label='cover_columns')
    
    plt.xlabel('Matrix Size')
    plt.ylabel('Speedup (Python time / C time)')
    plt.title('Performance Speedup of C vs Python Implementation')
    plt.xticks(range(len(sizes)), sizes)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add speedup values on top of bars
    for i, v in enumerate(min_col_speedups):
        plt.text(i - 0.2, v + 0.5, f'{v:.1f}x', ha='center')
    for i, v in enumerate(cover_cols_speedups):
        plt.text(i + 0.2, v + 0.5, f'{v:.1f}x', ha='center')
    
    plt.savefig('speedup_comparison.png')
    logger.info("Saved speedup comparison chart to 'speedup_comparison.png'")

def run_full_benchmark():
    """Run a comprehensive benchmark suite"""
    logger.info("Starting comprehensive benchmarks")
    
    # Test with random matrices of increasing size
    benchmark_scaling()
    
    # Test with real puzzle configurations
    for size in ['small', 'medium', 'large']:
        reset_performance_metrics()
        benchmark_with_real_puzzle(size)
    
    logger.info("Benchmark completed. See results above.")

def run_comparison_test():
    """Run a side-by-side comparison of Python and C implementations on the same inputs"""
    # Reset metrics
    reset_performance_metrics()
    
    # Create a medium-sized matrix for testing
    matrix, header = generate_test_matrix(1000, 200, 0.1)
    num_runs = 10
    
    logger.info(f"Running direct comparison with {len(matrix)}x{len(header)} matrix, {num_runs} iterations")
    
    # Test select_min_column
    logger.info("Testing select_min_column implementation:")
    py_results = []
    c_results = []
    
    py_start = time.time()
    for _ in range(num_runs):
        py_results.append(select_min_column_py(matrix, header))
    py_time = time.time() - py_start
    
    c_start = time.time()
    for _ in range(num_runs):
        c_results.append(select_min_column_c(matrix, header))
    c_time = time.time() - c_start
    
    results_match = all(p == c for p, c in zip(py_results, c_results))
    speedup = py_time / c_time if c_time > 0 else 0
    
    logger.info(f"select_min_column results match: {results_match}")
    logger.info(f"Python time: {py_time:.4f}s, C time: {c_time:.4f}s, Speedup: {speedup:.2f}x")
    
    # Show profiling report
    print_performance_report()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark Algorithm X implementations")
    parser.add_argument('--test', choices=['quick', 'full', 'compare'], default='compare',
                        help='Type of benchmark to run')
    args = parser.parse_args()
    
    if args.test == 'quick':
        benchmark_with_real_puzzle('small')
    elif args.test == 'full':
        run_full_benchmark()
    else:  # compare
        run_comparison_test()
    
    print_performance_report()
