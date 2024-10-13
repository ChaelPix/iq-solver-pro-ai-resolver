from piece import Piece, initialiser
from plateau import Plateau
import tkinter as tk

def main() -> None:
    root = tk.Tk()
    game = Plateau(root)
    pieces = initialiser()

    game.steps = [
                 [(pieces[0], (0, 0)), (pieces[2], (3, 5))],
                 [(pieces[1], (1, 2))],
                 [(pieces[2], (3, 5))],
                 [(pieces[3], (0, 0)), (pieces[2], (3, 5))],
                 [(pieces[4], (1, 2))],
                 [(pieces[5], (3, 5))],
                 [(pieces[6], (0, 0)), (pieces[2], (3, 5))],
                 [(pieces[7], (1, 2))],
                 [(pieces[8], (3, 5))],
                 [(pieces[9], (0, 0)), (pieces[2], (3, 5))],
                 [(pieces[9], (1, 2))],
                 [(pieces[10], (3, 5))],
                 [(pieces[11], (0, 0)), (pieces[2], (3, 5))]
                 ]

    game.update_board()
    root.mainloop()
    
if __name__ == "__main__":
    main()