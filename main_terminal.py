from piece import Piece
from plateau import Plateau

pieces = {}

piece_red = [
    [1, 1, 1, 1],
    [0, 0, 0, 1]
]
pieces["red"] = Piece("red", piece_red)

piece_orange = [
    [0, 1, 0],
    [1, 1, 1],
    [1, 0, 0]
]
pieces["orange"] = Piece("orange", piece_orange)

piece_yellow = [
    [1, 1, 1, 1],
    [0, 1, 0, 0]
]
pieces["yellow"] = Piece("yellow", piece_yellow)

piece_lime = [
    [1, 1, 1],
    [1, 0, 1]
]
pieces["lime"] = Piece("lime", piece_lime)

piece_green = [
    [1, 1, 1],
    [0, 1, 0]
]
pieces["green"] = Piece("green", piece_green)

piece_white = [
    [1, 1, 1],
    [0, 1, 1]
]
pieces["white"] = Piece("white", piece_white)

piece_cyan = [
    [0, 1],
    [1, 1]
]
pieces["cyan"] = Piece("cyan", piece_cyan)

piece_skyblue = [
    [1, 1, 1],
    [1, 0, 0],
    [1, 0, 0]
]
pieces["skyblue"] = Piece("skyblue", piece_skyblue)

piece_blue = [
    [0, 0, 1],
    [1, 1, 1]
]
pieces["blue"] = Piece("blue", piece_blue)

piece_purple = [
    [1, 1, 0],
    [0, 1, 1],
    [0, 0, 1]
]
pieces["purple"] = Piece("purple", piece_purple)

piece_darkred = [
    [0, 1, 1],
    [1, 1, 0]
]
pieces["darkred"] = Piece("darkred", piece_darkred)

piece_pink = [
    [1, 1, 0, 0],
    [0, 1, 1, 1]
]
pieces["pink"] = Piece("pink", piece_pink)


plateau = Plateau()

plateau.afficher()

success = plateau.placer_piece(pieces["red"], 0, (0, 0))
plateau.afficher()

success = plateau.placer_piece(pieces["red"], 1, (0, 0))
success = plateau.placer_piece(pieces["yellow"], 1, (3, 5))
plateau.afficher()

