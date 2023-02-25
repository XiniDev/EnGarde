import torch
import torch.nn as nn
import torch.nn.functional as F

import torch.optim as optim

from torch import Tensor

import numpy as np
import random

class LinearQNetwork(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int) -> None:
        super(LinearQNetwork, self).__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, output_size)

        self.output_size = output_size

    def forward(self, x: Tensor) -> Tensor:
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        # x = F.relu(self.linear3(x))
        x = self.linear3(x)
        
        # print(len(x))

        return x

class Trainer():
    def __init__(self, model: nn.Module, learning_rate: float, gamma: float, epsilon: float) -> None:
        self.model = model
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.optimizer = optim.Adam(model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()
        self.epsilon = epsilon
        self.epoch = 0

    def save(self, games: int, gap: int) -> None:
        self.epoch = int(games / gap)
        display_eps = int(round(self.epsilon, 3) * 1000)
        if display_eps == 0:
            display_eps = "000"
        elif display_eps < 10:
            display_eps = "00" + str(display_eps)
        elif display_eps < 100:
            display_eps = "0" + str(display_eps)
        path = f'./model/checkpoint_epo{self.epoch}_eps{display_eps}.pth'

        torch.save({
            'epoch': self.epoch,
            'epsilon': self.epsilon,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'loss': self.criterion,
            }, path)

    def load(self, path: str) -> None:
        checkpoint = torch.load(path)
        self.epoch = checkpoint['epoch']
        self.epsilon = checkpoint['epsilon']
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.criterion = checkpoint['loss']
        self.model.eval()

    def train(self, state: np.ndarray, action: int, reward: int, next_state: np.ndarray, hand: list[int]) -> None:
        state = torch.tensor(state, dtype=torch.float)
        # action = torch.tensor([action], dtype=torch.int)
        reward = torch.tensor([reward], dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)

        available_cards = [h for h in hand]
        available_cards = torch.tensor(available_cards, dtype=torch.long)

        mask = torch.zeros(self.model.output_size)
        mask[available_cards] = 1

        # no op
        if action == -1:
            Q_value = torch.zeros(self.model.output_size, requires_grad=True)
        else:
            Q_value = self.model(state)

            # Normalize Q-values using min-max normalization
            q_min = torch.min(Q_value)
            q_max = torch.max(Q_value)
            Q_value = (Q_value - q_min) / (q_max - q_min)

            # make unavailable actions 0 for loss calculation
            Q_value = Q_value * mask

        # print(self.model(next_state))
        Q_new_value = reward + self.gamma * torch.max(self.model(next_state))
        target = Q_value.clone()

        if action != -1:
            target[action] = Q_new_value
        # else:
        #     print(reward)
        #     print(Q_value)
        #     print(action)

        # print(Q_value, Q_new_value)
        # print(state)
        # print(next_state)
        # print(available_cards)
        # print(action)

        self.optimizer.zero_grad()
        loss = self.criterion(target, Q_value)
        loss.backward()
        # print(loss.item())
        self.optimizer.step()

    def predict(self, state: np.ndarray, hand: list[int]) -> int:
        if random.random() < self.epsilon:
            return int(random.random() * 4)
        else:
            available_cards = [h-1 for h in hand]
            # chooses between all the cards in deck, then picks the best move given on whats on hand
            state = torch.tensor(state, dtype=torch.float)
            available_cards = torch.tensor(available_cards, dtype=torch.long)

            Q_value = self.model(state)

            mask = torch.zeros_like(Q_value)
            mask[available_cards] = 1

            # Q_value = Q_value * mask

            # make them infinite instead of 0 because it uses argmax to calculate
            Q_value = torch.where(mask == 1, Q_value, torch.tensor(float('-inf'), device=Q_value.device))

            # print(hand)
            # print(mask)
            # print(Q_value)
            # print(torch.argmax(Q_value).item() + 1)

            # temp = Q_value.tolist()
            # res = np.array([x for i,x in enumerate(temp) if (i+1) in hand])
            # return np.argmax(res)

            res = torch.argmax(Q_value).item() + 1
            return hand.index(res)

    def update_epsilon(self, decay: float) -> None:
        self.epsilon *= decay

    # def predict(self, state: np.ndarray) -> int:
    #     state = torch.tensor(state, dtype=torch.float)
    #     Q_value = self.model(state)
    #     # print(Q_value)
    #     return torch.argmax(Q_value).item()

# STILL LEARNING :(

# RNN implementation

class RNNQNetwork(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int) -> None:
        super(RNNQNetwork, self).__init__()
        self.hidden_size = hidden_size
        self.rnn = nn.GRU(input_size, hidden_size)                                  # remembers the previous turn cards and deck etc, so dependencies between each turn is tracked compared to LinearQNetwork
        self.linear = nn.Linear(hidden_size, output_size)                           # linear here to map to output

    def forward(self, x: Tensor, h: Tensor) -> Tensor:
        out, h = self.rnn(x, h)
        out = self.linear(out[-1, :])
        return out, h

class RNNTrainer(Trainer):
    def __init__(self, model: nn.Module, learning_rate: float, gamma: float, epsilon: float) -> None:
        super(RNNTrainer, self).__init__(model, learning_rate, gamma, epsilon)
        self.h = None

    def train(self, state: np.ndarray, action: int, reward: int, next_state: np.ndarray) -> None:
        # no op
        if action == -1:
            return

        state = torch.tensor(state, dtype=torch.float)
        # action = torch.tensor([action], dtype=torch.int)
        reward = torch.tensor([reward], dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)

        if self.h is None:
            self.h = torch.zeros((1, self.model.hidden_size))

        Q_value, self.h = self.model(state, self.h)
        Q_new_value, _ = self.model(next_state, self.h)
        Q_new_value = reward + self.gamma * torch.max(Q_new_value)

        target = Q_value.clone()
        target[action] = Q_new_value

        self.optimizer.zero_grad()
        loss = self.criterion(target, Q_value)
        loss.backward()
        # print(loss.item())
        self.optimizer.step()

        self.h = self.h.detach()

    def predict(self, state: np.ndarray, hand: list[int]) -> int:
        if random.random() < self.epsilon:
            return int(random.random() * 4)
        else:
            # chooses between all the cards in deck, then picks the best move given on whats on hand
            state = torch.tensor(state, dtype=torch.float)
            Q_value, _ = self.model(state, torch.zeros((1, self.model.hidden_size)))
            temp = Q_value.tolist()
            res = np.array([x for i,x in enumerate(temp) if (i+1) in hand])
            return np.argmax(res)