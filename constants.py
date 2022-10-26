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