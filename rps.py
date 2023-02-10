import random

import numpy as np
import dqn as dqn

class Agent():
    def __init__(self, id: int) -> None:
        self.id = id
        self.move = 0

    def decision(self) -> int:
        # self.move += 1
        # if self.move > 2:
        #     self.move = 0
        choice = self.move
        return choice

class DQNAgent(Agent):
    def __init__(self, id: int) -> None:
        super().__init__(id)

        self.reward = 0
        self.old_state = None
        self.state = None

        self.reset_memory()

        self.model = dqn.Network(3, 128, 3)
        self.trainer = dqn.Trainer(self.model, 0.001, 0.9)
        self.epsilon = 0.9

    def reset_memory(self) -> None:
        self.state = [0, 0, 0]
        self.state = np.array(self.state, dtype=int)
    
    def get_state(self, opp_action: int) -> list[int]:
        if opp_action == 0:
            return [1, 0, 0]
        elif opp_action == 1:
            return [0, 1, 0]
        else:
            return [0, 0, 1]

    def get_reward(self, reward_score: int) -> int:
        reward = reward_score
        return reward

    def set_memory(self, reward_score: int, opp_action: int) -> None:
        self.old_state = self.state
        self.state = self.get_state(opp_action)
        self.state = np.array(self.state, dtype=int)
        
        self.reward = self.get_reward(reward_score)

        state = self.old_state
        action = self.move
        reward = self.reward
        new_state = self.state

        self.trainer.train(state, action, reward, new_state)

    def decision(self) -> int:
        if random.random() < self.epsilon:
            self.move = int(random.random() * 3)
        else:
            self.move = self.trainer.predict(self.state)
        # print(self.move)
        choice = self.move
        return choice

class GE():
    def __init__(self) -> None:
        self.ai_1 = DQNAgent(1)
        self.ai_2 = Agent(2)

        self.previous_winner = 0

        self.curr1 = 0
        self.curr2 = 0

    def game_loop(self) -> int:
        reward_score = self.previous_winner * 10 if self.previous_winner != 2 else -10
        self.ai_1.set_memory(reward_score, self.curr2)
        self.curr1 = self.ai_1.decision()
        self.curr2 = self.ai_2.decision()
        if self.curr1 == self.curr2:
            self.previous_winner = 0
        if self.curr1 == 0 and self.curr2 == 1:
            self.previous_winner = 2
        if self.curr1 == 1 and self.curr2 == 2:
            self.previous_winner = 2
        if self.curr1 == 2 and self.curr2 == 0:
            self.previous_winner = 2
        if self.curr1 == 0 and self.curr2 == 2:
            self.previous_winner = 1
        if self.curr1 == 1 and self.curr2 == 0:
            self.previous_winner = 1
        if self.curr1 == 2 and self.curr2 == 1:
            self.previous_winner = 1
        return self.previous_winner

ge = GE()
wins = [0, 0]
stop = False

while not stop:
    winner = ge.game_loop()
    if winner != 0:
        ge.ai_1.epsilon *= 0.9999
        wins[winner - 1] += 1
        print(f"Winner : AI {winner} | Wins: {wins} | Eps: {ge.ai_1.epsilon}")
    if 20000 in wins:
        print(f"Total Wins: {wins}")
        stop = True
