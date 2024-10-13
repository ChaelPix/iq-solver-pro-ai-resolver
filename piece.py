class Piece:
    def __init__(self, couleur, forme):
        self.couleur = couleur
        self.forme=forme

    def rotate(self):
        """Rotate the piece 90 degrees clockwise."""
        self.forme = [list(row) for row in zip(*self.forme[::-1])]
    def all_rotations(self):
        rotations = []
        current_forme = self.forme
        for _ in range(4):
            current_forme = [list(row) for row in zip(*current_forme[::-1])]
            rotations.append(current_forme)
        return rotations
    
    def display(self):
        """Display the piece"""
        
def initialiser() -> list:
    red = Piece("red",
    [[1, 1, 1, 1],
     [0, 0, 0, 1]])
    orange = Piece("orange",
    [[0, 1, 0],
    [1, 1, 1],
    [1, 0, 0]])
    yellow = Piece("yellow",
    [[1, 1, 1, 1],
     [0, 1, 0, 0]])
    lime = Piece("lime",
    [[1, 1, 1],
     [1, 0, 1]])
    green = Piece("green",
    [[1, 1, 1],
     [0, 1, 0]])
    white = Piece("white",
    [[1, 1, 1],
     [0, 1, 1]])
    cyan = Piece("cyan",
    [[0, 1],
    [1, 1]])
    skyblue = Piece("cadetblue2",
    [[1, 1, 1],
    [1, 0, 0],
    [1, 0, 0]])
    blue = Piece("blue",
    [[0, 0, 1],
     [1, 1, 1]])
    purple = Piece("purple",
    [[1, 1, 0],
     [0, 1, 1],
     [0, 0, 1]])
    darkred = Piece("darkred",
    [[0, 1, 1],
     [1, 1, 0]])
    pink = Piece("pink",
    [[1, 1, 0, 0],
     [0, 1, 1, 1]])
    return [red, orange, yellow, lime, green, white, cyan, skyblue, blue, purple, darkred, pink]
