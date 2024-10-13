from piece import Piece, initialiser
from plateau import Plateau


def main() -> None:
    Pieces = initialiser()
    for piece in Pieces:
        piece.display()
        print(piece.all_rotations())
        print()
    
    
if __name__ == "__main__":
    main()