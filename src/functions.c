#include <stdlib.h>
#include <stddef.h>
#include <limits.h>


typedef struct {
    int* values;
    size_t size;
} MatrixRow;

typedef struct {
    MatrixRow* rows;
    size_t row_count;
    size_t col_count;
} Matrix;

int find_min_column(Matrix* matrix) {
    if (matrix->row_count == 0 || matrix->col_count == 0)
        return -1;
        
    int* counts = (int*)calloc(matrix->col_count, sizeof(int));
    
    for (size_t r = 0; r < matrix->row_count; r++) {
        for (size_t c = 0; c < matrix->rows[r].size; c++) {
            if (matrix->rows[r].values[c] == 1 && c < matrix->col_count) {
                counts[c]++;
            }
        }
    }
    
    int min_count = INT_MAX;
    int min_col = -1;
    
    for (size_t c = 0; c < matrix->col_count; c++) {
        if (counts[c] > 0 && counts[c] < min_count) {
            min_count = counts[c];
            min_col = c;
        }
    }
    
    free(counts);
    return min_col;
}