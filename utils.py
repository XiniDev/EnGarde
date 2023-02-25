from action import *

# initialisation constants

SCALE = 1
ASPECT_RATIO = (16, 9)
WIDTH = 60 * ASPECT_RATIO[0] + 20 * ASPECT_RATIO[0] * SCALE
HEIGHT = 60 * ASPECT_RATIO[1] + 20 * ASPECT_RATIO[1] * SCALE
X_CENTER = WIDTH / 2
Y_CENTER = HEIGHT / 2

PISTE_LENGTH = 7
ACTIONS_MAX = 6

IMG_SCALE = U.SCALE * 3

ANIMATION_FRAMES = 20

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


def action_to_numeric(action: Action) -> int:
        numeric = 0
        match action:
            case Hit():
                numeric = 1
            case Smash():
                numeric = 2
            case Block():
                numeric = 3
            case Stance():
                numeric = 4
            case Blank():
                numeric = 5
            case Charge():
                numeric = 6
            case Push():
                numeric = 7
            case Forwards():
                numeric = 8
            case Backwards():
                numeric = 9
            case _:
                numeric = 0
        return numeric

def convert_binary(numbers: list[int], size: int) -> None:
    res = []
    for n in numbers:
        b = []
        binary = n
        for i in range(size):
            b.append(binary & 1)
            binary = binary >> 1
        res.extend(b[::-1])
    return res