#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>
#include <string.h>

/**
 * Find the column with the minimum number of 1s (MRV heuristic).
 * Optimized version using a faster counting approach.
 * 
 * @param rows_data Array of row data (1s and 0s for each column)
 * @param num_rows Number of rows in the matrix
 * @param num_cols Number of columns in the header
 * @return The index of the column with minimum count, or -1 if no valid column
 */
int select_min_column(int** rows_data, int num_rows, int num_cols) {
    if (num_rows == 0 || num_cols == 0) return -1;
    
    // Use stack allocation for small count arrays, heap for large ones
    int stack_counts[1024] = {0};  // Use stack for columns <= 1024
    int* counts = (num_cols <= 1024) ? stack_counts : (int*)calloc(num_cols, sizeof(int));
    
    if (counts == NULL && num_cols > 1024) return -1;  // Memory allocation failed
    
    // Count 1s in each column using cache-friendly traversal
    for (int c = 0; c < num_cols; c++) {
        int col_count = 0;
        for (int r = 0; r < num_rows; r++) {
            col_count += rows_data[r][c];
        }
        counts[c] = col_count;
    }
    
    // Find minimum non-zero count
    int min_count = INT_MAX;
    int min_idx = -1;
    
    for (int c = 0; c < num_cols; c++) {
        if (counts[c] > 0 && counts[c] < min_count) {
            min_count = counts[c];
            min_idx = c;
            
            // Early termination if we find a column with just one 1
            if (min_count == 1) break;
        }
    }
    
    // Free memory if we allocated on heap
    if (counts != stack_counts && num_cols > 1024) {
        free(counts);
    }
    
    return min_idx;
}

/**
 * Filter the matrix by removing rows that conflict with the selected row.
 * Optimized version using direct array operations.
 * 
 * @param rows_data Array of row data (1s and 0s)
 * @param num_rows Number of rows in the matrix
 * @param num_cols Number of columns in the header
 * @param columns_to_remove Array of column indices to check
 * @param num_columns_to_remove Number of columns in columns_to_remove
 * @param selected_row_idx Index of the selected row to remove
 * @param result_indices Output array where to store indices of kept rows
 * @return Number of rows kept in the result
 */
int cover_columns(int** rows_data, int num_rows, int num_cols,
                 int* columns_to_remove, int num_columns_to_remove,
                 int selected_row_idx, int* result_indices) {
    // Use a bitmap for faster exclusion checking
    char* bitmap = NULL;
    char stack_bitmap[8192] = {0}; // Use stack for moderate size (8K rows)
    int result_count = 0;
    
    // For smaller matrices, use stack allocation, otherwise use heap
    if (num_rows <= 8192) {
        bitmap = stack_bitmap;
        memset(bitmap, 0, num_rows);
    } else {
        bitmap = (char*)calloc(num_rows, sizeof(char));
        if (!bitmap) return 0;  // Memory allocation failed
    }
    
    // Mark selected row for exclusion
    bitmap[selected_row_idx] = 1;
    
    // Precompute column masks for faster checking
    for (int r = 0; r < num_rows; r++) {
        // Skip already excluded rows
        if (bitmap[r]) continue;
        
        // Check if row has a 1 in any excluded column
        for (int i = 0; i < num_columns_to_remove; i++) {
            int col_idx = columns_to_remove[i];
            if (rows_data[r][col_idx]) {
                bitmap[r] = 1;  // Mark for exclusion
                break;
            }
        }
    }
    
    // Collect indices of non-excluded rows
    for (int r = 0; r < num_rows; r++) {
        if (!bitmap[r]) {
            result_indices[result_count++] = r;
        }
    }
    
    // Free heap-allocated memory if used
    if (bitmap != stack_bitmap && num_rows > 8192) {
        free(bitmap);
    }
    
    return result_count;
}
