import tkinter as tk
from piece import Piece, initialiser

# Taille du plateau
ROWS, COLS = 5, 11

class Plateau:
    def __init__(self, root):
        self.root = root
        self.root.title("Quizler PRO")
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.current_step = 0  # Variable pour suivre l'état de l'algorithme
        
        # Création de la grille de jeu
        self.create_board()
        
        # Liste des étapes de l'algorithme
        self.steps = []  # Ce sera la liste des placements des pièces (à implémenter)
        
        # Boutons de contrôle
        self.create_controls()
    
    def create_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                frame = tk.Frame(self.root, width=40, height=40, bg="white", borderwidth=1, relief="solid")
                frame.grid(row=row, column=col)
                self.grid[row][col] = frame

    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.grid(row=ROWS, column=0, columnspan=COLS)
        
        # Boutons
        prev_button = tk.Button(control_frame, text="Précédent", command=self.previous_step)
        prev_button.pack(side=tk.LEFT)
        
        next_button = tk.Button(control_frame, text="Suivant", command=self.next_step)
        next_button.pack(side=tk.LEFT)
        
        finish_button = tk.Button(control_frame, text="Fin", command=self.go_to_end)
        finish_button.pack(side=tk.LEFT)
        
        reset_button = tk.Button(control_frame, text="Début", command=self.reset_board)
        reset_button.pack(side=tk.LEFT)
        
        # Curseur pour sélectionner les étapes
        self.step_slider = tk.Scale(control_frame, from_=0, to=0, orient=tk.HORIZONTAL, command=self.slider_update)
        self.step_slider.pack(side=tk.LEFT)
    
    def update_slider(self):
        self.step_slider.config(to=len(self.steps) - 1)
    
    def next_step(self):
        # Logique pour avancer d'une étape dans l'algorithme
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_board()

    def previous_step(self):
        # Logique pour revenir à l'étape précédente
        if self.current_step > 0:
            self.current_step -= 1
            self.update_board()

    def go_to_end(self):
        # Aller directement à la dernière étape
        self.current_step = len(self.steps) - 1
        self.update_board()

    def reset_board(self):
        # Réinitialiser le plateau
        self.current_step = 0
        self.update_board()

    def update_board(self):
        # Logique pour mettre à jour l'affichage du plateau en fonction de l'étape actuelle
        for row in range(ROWS):
            for col in range(COLS):
                self.grid[row][col].config(bg="grey")  # Reset all cells to white

        if self.current_step < len(self.steps):
            for piece, position in self.steps[self.current_step]:
                self.place_piece(piece, position)
        self.update_slider()

    def place_piece(self, piece, position):
        """Place a piece on the board at the given position."""
        if not self.check_valid_move(piece, position):
            return
        for i, row in enumerate(piece.forme):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[position[0] + i][position[1] + j].config(bg=piece.couleur)
                    
    def slider_update(self, value):
        self.current_step = int(value)
        self.update_board()

    def check_valid_move(self, piece, position):
        """Check if a piece can be placed at the given position."""
        for i, row in enumerate(piece.forme):
            for j, cell in enumerate(row):
                if cell:
                    if not (0 <= position[0] + i < ROWS and 0 <= position[1] + j < COLS):
                        return False
                    if self.grid[position[0] + i][position[1] + j].cget("bg") != "white":
                        return False
        return True