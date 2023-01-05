# THIS FILE WILL NOT BE PART OF THE CODE! IT IS ONLY A FILE TO LEARN HOW TO MAKE THE THING!

import torch
import torch.nn as nn
import torch.nn.functional as F

from torch import Tensor

import numpy as np

# hyperparameters ?????

GAMMA = 0.99                    # discount rate for computing temporal difference target
BATCH_SIZE = 32                 # transitions that will be sampled from the replay buffer when computing gradients
BUFFER_SIZE = 50000             # maximum number of transitions that will be stored
MIN_REPLAY_SIZE = 1000          # transitions that are in the replay buffer before computing gradients
EPSILON_START = 1.0             # starting value of epsilon (degree of explore / exploit)
EPSILON_END = 0.01              # ending value of epsilon
EPSILON_DECAY = 0.95            # decay rate of epsilon
LEARNING_RATE = 0.01            # how sensitive is the learning
TARGET_UPDATE_FREQ = 1000       # number of steps where target parameters is set to online parameters


# From:
# https://towardsdatascience.com/deep-deterministic-policy-gradients-explained-2d94655a9b7b
# Temporary just to see how ddpg works

class Critic(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int) -> None:
        super(Critic, self).__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, output_size)

    def forward(self, state: list[int], action: list[int]) -> Tensor:
        """
        Params state and actions are torch tensors
        """
        x = torch.cat([state, action], 1)
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = self.linear3(x)

        return x

class Actor(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int, learning_rate=3e-4) -> None:
        super(Actor, self).__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, output_size)
        
    def forward(self, state: list[int]):
        """
        Param state is a torch tensor
        """
        x = F.relu(self.linear1(state))
        x = F.relu(self.linear2(x))
        x = torch.tanh(self.linear3(x))

        return x

# from video youtube: https://www.youtube.com/watch?v=6Yd5WnYls_Y
# still learning how to make this

class Replay_Buffer():
    def __init__(self, memory_size: int, state_size: int, action_size: int) -> None:
        self.memory_size = memory_size
        self.memory_count = 0
        self.state_memory = np.zeros((memory_size, state_size))
        self.new_state_memory = np.zeros((memory_size, state_size))
        self.action_memory = np.zeros((memory_size, action_size))
        self.reward_memory = np.zeros(memory_size)
        
        self.terminal_memory = np.zeros(memory_size, dtype=np.float32)

    def store_transition(self, state: list[int], action: list[int], reward: int, new_state: list[int], done):
        index = self.memory_count % self.memory_size
        self.state_memory[index] = state
        self.action_memory[index] = action
        self.reward_memory[index] = reward
        self.new_state_memory[index] = new_state
        self.terminal_memory[index] = 1 - done
    
    def sample_buffer(self, batch_size):
        max_mem = min(self.memory_count, self.memory_size)
        batch = np.random.choice(max_mem, batch_size)

        states = self.state_memory[batch]
        actions = self.action_memory[batch]
        rewards = self.reward_memory[batch]
        new_states = self.new_state_memory[batch]

        terminal = self.terminal_memory[batch]

        return states, actions, rewards, new_states, terminal

class Trainer():
    def __init__(self, model: Network, gamma: float) -> None:
        self.gamma = gamma
        self.model = model

    def train(self, state: list[list[int]], action: list[int], reward: list[int], new_state: list[list[int]], turns: int) -> None:
        torch.tensor(state, dtype=torch.float)
        torch.tensor(action, dtype=torch.int)
        torch.tensor(reward, dtype=torch.float)
        torch.tensor(new_state, dtype=torch.float)

        result = self.model(state).clone()

        for i in range(turns):
            res = reward[i] + self.gamma * torch.max(self.model(new_state[i]))
            result[i][torch.argmax(action[i]).item()] = res

    def move_selection(self, state: list[int]) -> int:
        # action (max{Q(s',a)})
        state = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state)
        action = torch.argmax(prediction).item()
        return action

class DQN_Agent():
    def __init__(self) -> None:
        self.gamma = GAMMA
        self.epsilon = EPSILON_START
        self.model = Network(28, 256, 64, 4)
        self.trainer = Trainer(self.model, self.gamma)

        self.turn = 1
        self.memory = {}

    def set_memory(self, state: list[int], action: int, reward: int, new_state: list[int]) -> None:
        self.memory[self.turn] = (state, action, reward, new_state)
        self.turn += 1

    # def train(self, state: list[int], action: list[int], reward: list[int], new_state: list[int], turns: int) -> None:
    def train_n(self) -> None:
        states, actions, rewards, new_states = zip(*self.memory.values())
        self.trainer.train(states, actions, rewards, new_states, self.turn)
    
    def train(self, state: list[int], action: int, reward: int, new_state: list[int]):
        self.trainer(state, action, reward, new_state, 1)
