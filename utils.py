from action import *

# initialisation constants

SCALE = 8
WIDTH = 160 * SCALE
HEIGHT = 90 * SCALE
X_CENTER = WIDTH / 2
Y_CENTER = HEIGHT / 2

# actions

ACTION_SYMBOLS = ['x', 'X', 'b', 'B', '_', '-', '=', '>', '<']
ALL_MOVES_STR = {
    "Lunge" : "--=x__",
    "Parry" : "BBBB",
    "Riposte" : "bb__x_",
    "Thrust" : "-x__",
    "Flèche" : "---=X___",
    "Fake" : "--",
    "Dodge" : "_<",
    "Move" : "_>"
}


ALL_MOVES = {}

# load ALL_MOVES function

def load_ALL_MOVES() -> None:
    global ALL_MOVES
    for (name, move_str) in ALL_MOVES_STR.items():
        actions = []
        for action in move_str:
            match action:
                case 'x':
                    actions.append(Hit())
                case 'X':
                    actions.append(Smash())
                case 'b':
                    actions.append(Block())
                case 'B':
                    actions.append(Stance())
                case '_':
                    actions.append(Blank())
                case '-':
                    actions.append(Charge())
                case '=':
                    actions.append(Push())
                case '>':
                    actions.append(Forwards())
                case '<':
                    actions.append(Backwards())
        ALL_MOVES[name] = tuple(actions)
    print(ALL_MOVES)