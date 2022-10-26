import constants as A

# action class

class Action():
    def __init__(self, symbol: str) -> None:
        self.symbol = None
        try:
            if symbol in A.ACTION_SYMBOLS:
                self.symbol = symbol
            else:
                raise ValueError('Actions must have a valid symbol')
        except ValueError as exp:
            print("An action used an invalid symbol: {}\n{}".format(symbol, exp))
            exit(1)
        
        self.state = {}

class Hit(Action):
    def __init__(self) -> None:
        super().__init__('x')
        self.state['score'] = False
    
    def reset_states(self) -> None:
        self.state['score'] = False
    
    def check(self, action: Action, distance: int) -> None:
        self.reset_states()
        if distance == 0:
            self.state['score'] = True
            match action:
                case Hit():
                    self.state['score'] = False                 # fix later (charge)
                case Smash() | Block() | Stance():
                    self.state['score'] = False

    def resolve(self, action: Action, distance: int) -> None:
        pass

class Smash(Action):
    def __init__(self) -> None:
        super().__init__('X')
        self.state['score'] = False
        self.state['move'] = True
        self.state['push'] = False
    
    def reset_states(self) -> None:
        self.state['score'] = False
        self.state['move'] = True
        self.state['push'] = False
    
    def check(self, action: Action, distance: int) -> None:
        self.reset_states()
        if distance == 0:
            self.state['score'] = True
            self.state['push'] = True
        match action:
            case Smash():
                self.state['score'] = False
                self.state['move'] = False if distance <= 1 else True
                self.state['push'] = False
            case Block():
                self.state['score'] = False
                self.state['move'] = True
                self.state['push'] = True if distance == 0 else False
            case Stance():
                self.state['score'] = False
                self.state['move'] = False if distance == 0 else True
                self.state['push'] = False

    def resolve(self, action: Action, distance: int) -> None:
        pass

class Block(Action):
    def __init__(self) -> None:
        super().__init__('b')
        # potentially add stutter for smash vs block animation
    
    def reset_states(self) -> None:
        pass
    
    def check(self, action: Action, distance: int) -> None:
        self.reset_states()
        pass

    def resolve(self, action: Action, distance: int) -> None:
        pass

class Stance(Action):
    def __init__(self) -> None:
        super().__init__('B')
    
    def reset_states(self) -> None:
        pass
    
    def check(self, action: Action, distance: int) -> None:
        self.reset_states()
        pass

    def resolve(self, action: Action, distance: int) -> None:
        pass

class Blank(Action):
    def __init__(self) -> None:
        super().__init__('_')
    
    def reset_states(self) -> None:
        pass
    
    def check(self, action: Action, distance: int) -> None:
        self.reset_states()
        pass

    def resolve(self, action: Action, distance: int) -> None:
        pass

class Charge(Action):
    def __init__(self) -> None:
        super().__init__('-')
    
    def reset_states(self) -> None:
        pass
    
    def check(self, action: Action, distance: int) -> None:
        self.reset_states()
        pass

    def resolve(self, action: Action, distance: int) -> None:
        pass

class Push(Action):
    def __init__(self) -> None:
        super().__init__('=')
        self.state['move'] = True
        self.state['push'] = False
    
    def reset_states(self) -> None:
        self.state['move'] = True
        self.state['push'] = False
    
    def check(self, action: Action, distance: int) -> None:
        self.reset_states()
        if distance == 0:
            self.state['push'] = True
        match action:
            case Smash() | Push():
                self.state['move'] = False if distance <= 1 else True
                self.state['push'] = False
            case Stance():
                self.state['move'] = False if distance == 0 else True
                self.state['push'] = False

    def resolve(self, action: Action, distance: int) -> None:
        pass

class Forwards(Action):
    def __init__(self) -> None:
        super().__init__('>')
        self.state['move'] = True
    
    def reset_states(self) -> None:
        self.state['move'] = True
    
    def check(self, action: Action, distance: int) -> None:
        self.reset_states()
        if distance == 0:
            self.state['move'] = False
        elif distance <= 1:
            match action:
                case Smash() | Push():
                    self.state['move'] = False
                case Forwards():
                    self.state['move'] = False

    def resolve(self, action: Action, distance: int) -> None:
        pass

class Backwards(Action):
    def __init__(self) -> None:
        super().__init__('<')
        self.state['move'] = True
    
    def reset_states(self) -> None:
        self.state['move'] = True
    
    def check(self, action: Action, distance: int) -> None:
        self.reset_states()
        pass

    def resolve(self, action: Action, distance: int) -> None:
        pass
