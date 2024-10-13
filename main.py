from piece import Piece, initialiser
from plateau import Plateau
import tkinter as tk


def main() -> None:
    # Initialize the root window
    root = tk.Tk()

    # Create the Plateau instance
    game = Plateau(root)

    # Initialize pieces
    pieces = initialiser()

    # Define some demo steps
    game.steps = [
        [(pieces[0], (0, 0)), (pieces[2], (3, 5))],  # Place the first piece at the top-left corner
        [(pieces[1], (1, 2))],  # Place the second piece at position (1, 2)
        [(pieces[2], (3, 5))],  # Place the third piece at position (3, 5)
    ]

    # Start the main loop
    root.mainloop()
    
    
if __name__ == "__main__":
    main()