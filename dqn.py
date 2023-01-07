import torch
import torch.nn as nn
import torch.nn.functional as F

from torch import Tensor

import numpy as np

class Network(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int) -> None:
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, output_size)

    def forward(self, x: Tensor) -> Tensor:
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = self.linear3(x)

        return x

class Trainer():
    def __init__(self, model: Network, learning_rate: float, gamma: float) -> None:
        self.model = model
        self.learning_rate = learning_rate
        self.gamma = gamma
        # self.optimizer = >??
        # self.criterion = nn.MSELoss()

    def train(self, state: np.ndarray, action: int, reward: int, next_state: np.ndarray) -> None:
        state = torch.tensor(state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.int)
        reward = torch.tensor(reward, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)

        Q_value = self.model(state)
        Q_new_value = reward + self.gamma * torch.max(self.model(next_state))
        target = Q_value.clone()
        target[torch.argmax(action).item()] = Q_new_value


# STILL LEARNING :(