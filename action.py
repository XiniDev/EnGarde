import utils as U

# action class

class Action():
    def __init__(self, symbol: str) -> None:
        self.symbol = None
        try:
            if symbol in U.ACTION_SYMBOLS:
                self.symbol = symbol
            else:
                raise ValueError('Actions must have a valid symbol')
        except ValueError as exp:
            print("An action used an invalid symbol: {}\n{}".format(symbol, exp))
            exit(1)
        
        self.SCORE = 0
        self.IS_X = 0
        self.CHARGE = 0
        self.PUSH = 0
        self.MOVE = 0

        self.BLOCK = 1
        self.STANCE = 1

        # execute a particular element of this action?
        self.x_score = 0
        self.x_move = 0
        self.x_push = 0

    def __repr__(self) -> str:
        return type(self).__name__

class Hit(Action):
    def __init__(self) -> None:
        super().__init__('x')
        self.SCORE = 1
        self.IS_X = 1

class Smash(Action):
    def __init__(self) -> None:
        super().__init__('X')
        self.SCORE = 1.5
        self.IS_X = 1
        self.PUSH = 1.5
        self.MOVE = 1

class Block(Action):
    def __init__(self) -> None:
        super().__init__('b')
        # potentially add stutter for smash vs BLOCK animation
        self.BLOCK = 0

class Stance(Action):
    def __init__(self) -> None:
        super().__init__('B')
        self.BLOCK = 0
        self.STANCE = 0

class Blank(Action):
    def __init__(self) -> None:
        super().__init__('_')

class Charge(Action):
    def __init__(self) -> None:
        super().__init__('-')
        self.CHARGE = 1

class Push(Action):
    def __init__(self) -> None:
        super().__init__('=')
        self.CHARGE = 1
        self.PUSH = 1
        self.MOVE = 1

class Forwards(Action):
    def __init__(self) -> None:
        super().__init__('>')
        self.MOVE = 1

class Backwards(Action):
    def __init__(self) -> None:
        super().__init__('<')
        self.MOVE = -1