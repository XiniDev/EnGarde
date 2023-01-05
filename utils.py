from action import *

# initialisation constants

SCALE = 8
WIDTH = 160 * SCALE
HEIGHT = 90 * SCALE
X_CENTER = WIDTH / 2
Y_CENTER = HEIGHT / 2

PISTE_LENGTH = 7
ACTIONS_MAX = 6

# actions

ACTION_SYMBOLS = ['x', 'X', 'b', 'B', '_', '-', '=', '>', '<']
ALL_MOVES_STR = {
    1: ("Lunge", "--=x__"),
    2: ("Parry", "BBBB"),
    3: ("Riposte", "bb__x_"),
    4: ("Thrust", "-x__"),
    5: ("Flèche", "---=X___"),
    6: ("Fake", "--"),
    7: ("Dodge", "_<"),
    8: ("Move", "_>")
}


ALL_MOVES = {}

# load ALL_MOVES function

def load_ALL_MOVES() -> None:
    global ALL_MOVES
    for (id, move_info) in ALL_MOVES_STR.items():
        actions = []
        for action in move_info[1]:
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
        ALL_MOVES[id] = (move_info[0], tuple(actions))
    print(ALL_MOVES)


def convert_action(symbol: str) -> Action:
    match symbol:
        case 'x':
            return Hit()
        case 'X':
            return Smash()
        case 'b':
            return Block()
        case 'B':
            return Stance()
        case '_':
            return Blank()
        case '-':
            return Charge()
        case '=':
            return Push()
        case '>':
            return Forwards()
        case '<':
            return Backwards()