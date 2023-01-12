import pygame
import random

from collections import deque

import utils as U

class Move():
    def __init__(self, id: int, ALL_MOVES: dict) -> None:
        self.id = None
        try:
            if id in ALL_MOVES:
                self.id = id
            else:
                raise ValueError('Moves must have a valid id')
        except ValueError as exp:
            print("The move: {} does not have a valid id\n{}".format(id, exp))
            exit(1)

        self.name = ALL_MOVES.get(self.id)[0]

        self.actions = ALL_MOVES.get(self.id)[1]

        self.slots = len(self.actions)

    def __repr__(self) -> str:
        return (f"Move: {self.name} | Actions: {self.actions}")
    
    def split(self, value: int) -> None:
        if value > 0:
            return [self.actions[0:value], self.actions[value:]]           # split on value, [first half, second half]
        else:
            return [self.actions, []]


# card engine class

class Card_Engine():
    def __init__(self, no_shuffle=False) -> None:
        self.DECK_MAX = 8
        self.HAND_MAX = 4
        self.deck = deque()
        self.hand = []

        self.no_shuffle = no_shuffle
    
    def reset(self) -> None:
        self.deck_add_moves(self.hand)
        self.hand = []
        self.deck_shuffle()
        self.draw_moves()

    def reset_cards(self) -> None:
        self.deck = deque()
        self.hand = []
    
    def start(self, ALL_MOVES: dict) -> None:
        self.reset_cards()

        # example moves
        moves = []
        for id in ALL_MOVES:
            moves.append(Move(id, ALL_MOVES))
        self.deck_add_moves(moves)
        
        self.deck_shuffle()
        self.draw_moves()

    def deck_size_check(self, addition: int) -> bool:
        return (len(self.deck) + addition <= self.DECK_MAX)

    def deck_add_move(self, move: Move) -> bool:
        if self.deck_size_check(1):
            self.deck.append(move)
            return True
        else:
            return False

    def deck_add_moves(self, moves: list[Move]) -> bool:
        if self.deck_size_check(len(moves)):
            self.deck.extend(moves)
            return True
        else:
            return False

    def deck_shuffle(self) -> None:
        if not self.no_shuffle:
            random.shuffle(self.deck)

    def draw_move(self) -> None:
        move = self.deck.popleft()
        if len(self.hand) == self.HAND_MAX - 1:
            self.hand.append(move)

    def draw_moves(self) -> None:
        if len(self.hand) == self.HAND_MAX - self.HAND_MAX:
            self.hand.extend([self.deck.popleft() for i in range(self.HAND_MAX)])

    def play_move(self, move_id: int) -> Move:       # three moves to choose from, after select one with mouse, it should give the number of the item in the hand
        # print(move_id, self.hand)
        move = self.hand[move_id]
        self.hand[move_id] = self.deck.popleft()
        self.deck.append(move)
        return move

class Card_Engine_Display(Card_Engine):
    def __init__(self, no_shuffle=False) -> None:
        super().__init__(no_shuffle)
        self.cards = [None, None, None, None]
    
    def update(self, win: pygame.Surface) -> None:
        self.draw(win)
    
    def draw(self, win: pygame.Surface) -> None:
        size = (200, 100)
        card_button = pygame.Surface(size)
        card_button.fill((128, 128, 128))

        # setting x values for drawing the cards in this order : 3, 1, 2, 4, then sorting it        
        x_value = sorted([U.X_CENTER - size[0] - 50 - (((i + 1) // 2) * 300 * (-1 if i % 2 == 1 else 1)) for i in range(self.HAND_MAX)])
        
        for i in range(self.HAND_MAX):
            self.cards[i] = win.blit(card_button, (x_value[i], 500))

        for i in range(self.HAND_MAX):
            win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Move: " + str(self.hand[i].name), False, (255, 255, 255)), (x_value[i], 500))
            win.blit(pygame.font.SysFont('Comic Sans MS', 18).render(str([action.symbol for action in self.hand[i].actions]), False, (255, 255, 255)), (x_value[i], 600))