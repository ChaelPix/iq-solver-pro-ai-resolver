#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>

// Structure for a node in the Dancing Links matrix
typedef struct Node {
    struct Node *left, *right, *up, *down;
    struct Node *column;
    int row_id;      // ID of the row this node belongs to
    int col_id;      // ID of the column this node belongs to
    int size;        // For column headers: number of nodes in this column
} Node;

// Structure for the DLX solver state
typedef struct {
    Node *header;               // Root of the dancing links structure
    int *solution;              // Array to store row indices in the solution
    int solution_count;         // Number of rows in the solution
    int max_solutions;          // Maximum number of solutions to find
    int total_rows;             // Total number of rows in the matrix
    int total_columns;          // Total number of columns in the matrix
    int solutions_found;        // Number of solutions found so far
    int branches_explored;      // Number of branches explored
    int branches_pruned;        // Number of branches pruned
    int placements_tested;      // Number of placements tested
    bool stop_requested;        // Flag to stop the algorithm
    void (*callback)(int*, int); // Callback function to report solutions
} DLX;

// Create a column header
Node* create_column_header(int col_id) {
    Node *col = (Node*)malloc(sizeof(Node));
    col->left = col;
    col->right = col;
    col->up = col;
    col->down = col;
    col->column = col;
    col->row_id = -1;
    col->col_id = col_id;
    col->size = 0;
    return col;
}

// Create a new node in the matrix
Node* create_node(int row_id, Node *column) {
    Node *node = (Node*)malloc(sizeof(Node));
    node->row_id = row_id;
    node->column = column;
    node->col_id = column->col_id;
    
    // Link the node vertically into the column
    node->up = column->up;
    node->down = column;
    column->up->down = node;
    column->up = node;
    
    // Increment column size
    column->size++;
    
    return node;
}

// Initialize the DLX structure
DLX* init_dlx(int num_columns, int max_solutions) {
    DLX *dlx = (DLX*)malloc(sizeof(DLX));
    if (!dlx) return NULL;
    
    // Create header node (root)
    Node *header = create_column_header(-1);
    dlx->header = header;
    
    // Create and link column headers
    Node *prev = header;
    for (int i = 0; i < num_columns; i++) {
        Node *col = create_column_header(i);
        
        // Link column horizontally
        col->right = prev->right;
        col->left = prev;
        prev->right->left = col;
        prev->right = col;
        
        prev = col;
    }
    
    // Initialize other fields
    dlx->solution = NULL;
    dlx->solution_count = 0;
    dlx->max_solutions = max_solutions;
    dlx->total_rows = 0;
    dlx->total_columns = num_columns;
    dlx->solutions_found = 0;
    dlx->branches_explored = 0;
    dlx->branches_pruned = 0;
    dlx->placements_tested = 0;
    dlx->stop_requested = false;
    dlx->callback = NULL;
    
    return dlx;
}

// Add a row to the DLX structure
void add_row(DLX *dlx, int row_id, int *row_data) {
    Node *prev = NULL;
    
    for (int j = 0; j < dlx->total_columns; j++) {
        if (row_data[j] == 1) {
            // Find the column header
            Node *col = dlx->header;
            for (int k = 0; k <= j; k++) {
                col = col->right;
                if (col == dlx->header) {
                    // Wrap around if needed
                    col = col->right;
                }
            }
            
            // Create a new node
            Node *node = create_node(row_id, col);
            
            // Link horizontally if we have a previous node
            if (prev) {
                node->right = prev->right;
                node->left = prev;
                prev->right->left = node;
                prev->right = node;
            } else {
                // This is the first node in the row
                node->right = node;
                node->left = node;
            }
            
            prev = node;
        }
    }
    
    dlx->total_rows++;
}

// Cover a column (remove from available columns)
void cover_column(Node *col) {
    // Unlink column header
    col->right->left = col->left;
    col->left->right = col->right;
    
    // Iterate through rows in this column
    for (Node *row = col->down; row != col; row = row->down) {
        // Remove this row from other columns it occupies
        for (Node *right = row->right; right != row; right = right->right) {
            right->up->down = right->down;
            right->down->up = right->up;
            right->column->size--;
        }
    }
}

// Uncover a column (undo cover operation)
void uncover_column(Node *col) {
    // Iterate through rows in this column, in reverse order
    for (Node *row = col->up; row != col; row = row->up) {
        // Restore this row to other columns it occupies
        for (Node *left = row->left; left != row; left = left->left) {
            left->column->size++;
            left->up->down = left;
            left->down->up = left;
        }
    }
    
    // Relink column header
    col->right->left = col;
    col->left->right = col;
}

// Find column with minimum size (MRV heuristic)
Node* get_min_column(DLX *dlx) {
    Node *min_col = NULL;
    int min_size = __INT_MAX__;
    
    for (Node *col = dlx->header->right; col != dlx->header; col = col->right) {
        if (col->size < min_size) {
            min_size = col->size;
            min_col = col;
            if (min_size == 0) {
                break; // This column is empty, can't proceed
            }
        }
    }
    
    return min_col;
}

// Recursive search function for the DLX algorithm
bool search(DLX *dlx, int depth) {
    dlx->branches_explored++;
    
    // Check if we should stop
    if (dlx->stop_requested) {
        return false;
    }
    
    // If no more columns to cover, we found a solution
    if (dlx->header->right == dlx->header) {
        // Copy the current solution if callback is set
        if (dlx->callback) {
            dlx->callback(dlx->solution, dlx->solution_count);
        }
        dlx->solutions_found++;
        return true;
    }
    
    // Choose column with minimum size (MRV heuristic)
    Node *col = get_min_column(dlx);
    
    // If a column has no 1s, this branch has no solution
    if (col == NULL || col->size == 0) {
        dlx->branches_pruned++;
        return false;
    }
    
    // Cover the chosen column
    cover_column(col);
    
    bool result = false;
    
    // Try each row in this column
    for (Node *row = col->down; row != col; row = row->down) {
        dlx->placements_tested++;
        
        // Add this row to the solution
        dlx->solution[depth] = row->row_id;
        dlx->solution_count = depth + 1;
        
        // Cover all columns that are covered by this row
        for (Node *right = row->right; right != row; right = right->right) {
            cover_column(right->column);
        }
        
        // Recursively search
        if (search(dlx, depth + 1)) {
            result = true;
            if (dlx->solutions_found >= dlx->max_solutions) {
                break;  // Stop if we've found enough solutions
            }
        }
        
        // Backtrack: uncover all columns covered by this row
        for (Node *left = row->left; left != row; left = left->left) {
            uncover_column(left->column);
        }
    }
    
    // Uncover the chosen column
    uncover_column(col);
    return result;
}

// Start the DLX solving process
int solve_dlx(DLX *dlx, void (*callback)(int*, int)) {
    // Allocate memory for solution array
    dlx->solution = (int*)malloc(dlx->total_rows * sizeof(int));
    if (!dlx->solution) return -1;
    
    dlx->solution_count = 0;
    dlx->solutions_found = 0;
    dlx->callback = callback;
    
    // Start the search
    search(dlx, 0);
    
    return dlx->solutions_found;
}

// Free all memory used by the DLX structure
void free_dlx(DLX *dlx) {
    if (!dlx) return;
    
    // Free all nodes in the structure
    Node *curr_col = dlx->header->right;
    while (curr_col != dlx->header) {
        Node *next_col = curr_col->right;
        
        // Free nodes in this column
        Node *curr_node = curr_col->down;
        while (curr_node != curr_col) {
            Node *next_node = curr_node->down;
            free(curr_node);
            curr_node = next_node;
        }
        
        free(curr_col);
        curr_col = next_col;
    }
    
    // Free header node
    free(dlx->header);
    
    // Free solution array
    free(dlx->solution);
    
    // Free DLX structure
    free(dlx);
}

// Request to stop the algorithm
void request_stop(DLX *dlx) {
    dlx->stop_requested = true;
}

// Get statistics from the DLX solver
void get_stats(DLX *dlx, int *branches_explored, int *branches_pruned, 
               int *placements_tested, int *solutions_found) {
    *branches_explored = dlx->branches_explored;
    *branches_pruned = dlx->branches_pruned;
    *placements_tested = dlx->placements_tested;
    *solutions_found = dlx->solutions_found;
}

/**
 * C API functions for Python integration
 */

// Create a new DLX solver
DLX* dlx_create(int num_columns, int max_solutions) {
    return init_dlx(num_columns, max_solutions);
}

// Add a row to the matrix
void dlx_add_row(DLX *dlx, int row_id, int *row_data) {
    add_row(dlx, row_id, row_data);
}

// Solve the DLX matrix
int dlx_solve(DLX *dlx, void (*callback)(int*, int)) {
    return solve_dlx(dlx, callback);
}

// Release resources
void dlx_free(DLX *dlx) {
    free_dlx(dlx);
}

// Stop the solver
void dlx_stop(DLX *dlx) {
    request_stop(dlx);
}

// Get solver statistics
void dlx_get_stats(DLX *dlx, int *stats) {
    get_stats(dlx, &stats[0], &stats[1], &stats[2], &stats[3]);
}
