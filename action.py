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
        
        self.attributes = {
            'score' : 0,
            'is_x' : 0,
            'charge' : 0,

            'push' : 0,
            'move' : 0,

            'block': 1,
            'stance': 1
        }

        self.states = {}
    
    def check(self, index: int, states: dict) -> None:
        for k, v in states.items():
            self.states[k] = v[index]

class Hit(Action):
    def __init__(self) -> None:
        super().__init__('x')
        self.attributes['score'] = 1
        self.attributes['is_x'] = 1
    
    # def reset_states(self) -> None:
    #     self.states['score'] = False
    
    # def check(self, action: Action, distance: int) -> None:
    #     self.reset_states()
    #     if distance == 0:
    #         self.states['score'] = True
    #         match action:
    #             case Hit():
    #                 self.states['score'] = False                 # fix later (charge)
    #             case Smash() | Block() | Stance():
    #                 self.states['score'] = False

    # def resolve(self, action: Action, distance: int) -> None:
    #     pass

class Smash(Action):
    def __init__(self) -> None:
        super().__init__('X')
        self.attributes['score'] = 1.5
        self.attributes['is_x'] = 1
        self.attributes['push'] = 1.5
        self.attributes['move'] = 1
    
    # def reset_states(self) -> None:
    #     self.states['score'] = False
    #     self.states['move'] = True
    #     self.states['push'] = False
    
    # def check(self, action: Action, distance: int) -> None:
    #     self.reset_states()
    #     if distance == 0:
    #         self.states['score'] = True
    #         self.states['push'] = True
    #     match action:
    #         case Smash():
    #             self.states['score'] = False
    #             self.states['move'] = False if distance <= 1 else True
    #             self.states['push'] = False
    #         case Block():
    #             self.states['score'] = False
    #             self.states['move'] = True
    #             self.states['push'] = True if distance == 0 else False
    #         case Stance():
    #             self.states['score'] = False
    #             self.states['move'] = False if distance == 0 else True
    #             self.states['push'] = False

    # def resolve(self, action: Action, distance: int) -> None:
    #     pass

class Block(Action):
    def __init__(self) -> None:
        super().__init__('b')
        # potentially add stutter for smash vs block animation
        self.attributes['block'] = 0
    
    # def reset_states(self) -> None:
    #     pass
    
    # def check(self, action: Action, distance: int) -> None:
    #     self.reset_states()
    #     pass

    # def resolve(self, action: Action, distance: int) -> None:
    #     pass

class Stance(Action):
    def __init__(self) -> None:
        super().__init__('B')
        self.attributes['block'] = 0
        self.attributes['stance'] = 0
    
    # def reset_states(self) -> None:
    #     pass
    
    # def check(self, action: Action, distance: int) -> None:
    #     self.reset_states()
    #     pass

    # def resolve(self, action: Action, distance: int) -> None:
    #     pass

class Blank(Action):
    def __init__(self) -> None:
        super().__init__('_')
    
    # def reset_states(self) -> None:
    #     pass
    
    # def check(self, action: Action, distance: int) -> None:
    #     self.reset_states()
    #     pass

    # def resolve(self, action: Action, distance: int) -> None:
    #     pass

class Charge(Action):
    def __init__(self) -> None:
        super().__init__('-')
        self.attributes['charge'] = 1
    
    # def reset_states(self) -> None:
    #     pass
    
    # def check(self, action: Action, distance: int) -> None:
    #     self.reset_states()
    #     pass

    # def resolve(self, action: Action, distance: int) -> None:
    #     pass

class Push(Action):
    def __init__(self) -> None:
        super().__init__('=')
        self.attributes['charge'] = 1
        self.attributes['push'] = 1
        self.attributes['move'] = 1
    
    # def reset_states(self) -> None:
    #     self.states['move'] = True
    #     self.states['push'] = False
    
    # def check(self, action: Action, distance: int) -> None:
    #     self.reset_states()
    #     if distance == 0:
    #         self.states['push'] = True
    #     match action:
    #         case Smash() | Push():
    #             self.states['move'] = False if distance <= 1 else True
    #             self.states['push'] = False
    #         case Stance():
    #             self.states['move'] = False if distance == 0 else True
    #             self.states['push'] = False

    # def resolve(self, action: Action, distance: int) -> None:
    #     pass

class Forwards(Action):
    def __init__(self) -> None:
        super().__init__('>')
        self.attributes['move'] = 1
    
    # def reset_states(self) -> None:
    #     self.states['move'] = True
    
    # def check(self, action: Action, distance: int) -> None:
    #     self.reset_states()
    #     if distance == 0:
    #         self.states['move'] = False
    #     elif distance <= 1:
    #         match action:
    #             case Smash() | Push():
    #                 self.states['move'] = False
    #             case Forwards():
    #                 self.states['move'] = False

    # def resolve(self, action: Action, distance: int) -> None:
    #     pass

class Backwards(Action):
    def __init__(self) -> None:
        super().__init__('<')
        self.attributes['move'] = -1
    
    # def reset_states(self) -> None:
    #     self.states['move'] = True
    
    # def check(self, action: Action, distance: int) -> None:
    #     self.reset_states()
    #     pass

    # def resolve(self, action: Action, distance: int) -> None:
    #     pass

# action logic

class Action_Logic():
    def __init__(self) -> None:
        self.reach = 0

        self.states = {}
    
    def compute(self, a_1: Action, a_2: Action, distance: int, charge: list[int]) -> list[int]:
        self.reset_states()
        self.set_reach(a_1, a_2, distance)
        self.states['score'] = self.score_function(a_1, a_2, charge)
        charge = self.set_charge(a_1, a_2, charge)
        self.states['push'] = self.push_function(a_1, a_2)
        self.states['move'] = self.move_function(a_1, a_2, self.states['push'])
        a_1.check(0, self.states)
        a_2.check(1, self.states)
        return charge
    
    def reset_states(self) -> None:
        self.states.clear()
    
    def set_reach(self, a_1: Action, a_2: Action, distance: int) -> None:
        self.reach = -distance + a_1.attributes['move'] + a_2.attributes['move']

    def set_charge(self, a_1: Action, a_2: Action, charge: list[int]) -> list[int]:
        return [charge[0] + a_1.attributes['charge'] if a_1.attributes['charge'] == 1 else 0, charge[1] + a_2.attributes['charge'] if a_2.attributes['charge'] == 1 else 0]

    def score_function(self, a_1: Action, a_2: Action, charge: list[int]) -> list[int]:
        winner = (charge[0] + a_1.attributes['score']) * a_1.attributes['is_x'] - (charge[1] + a_2.attributes['score']) * a_2.attributes['is_x']
        reach = self.reach + 1
        res = winner * reach
        check_condition = (a_1.attributes['is_x'] + a_2.attributes['is_x']) * reach * (a_1.attributes['block'] * a_2.attributes['block'])
        if check_condition > 0:
            return [1, 1] if res == 0 else [1 if res > 0 else 0, 1 if res < 0 else 0]
        else:
            return [0, 0]
        # if res == 0:
        #     return [1, 1] if check_condition > 0 else [0, 0]
        # else:
        #     return [1 if res > 0 else 0, 1 if res < 0 else 0]

    def push_function(self, a_1: Action, a_2: Action) -> list[int]:
        winner = (a_1.attributes['push'] - a_2.attributes['push'])
        reach = self.reach
        res = winner * reach
        check_condition = reach * (a_1.attributes['stance'] * a_2.attributes['stance'])
        if check_condition > 0:
            return [1 if res > 0 else 0, 1 if res < 0 else 0]
        else:
            return [0, 0]

    def move_function(self, a_1: Action, a_2: Action, push: list[int]) -> list[int]:
        reach = -self.reach + 1
        if 1 in push:
            return push
        else:
            return [a_1.attributes['move'] if reach > 0 else 0, a_2.attributes['move'] if reach > 0 else 0]