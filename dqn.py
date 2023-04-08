import torch
import torch.nn as nn
import torch.nn.functional as F

import torch.optim as optim

from torch import Tensor

import numpy as np
import random

class Trainer():
    def __init__(self, model: nn.Module, learning_rate: float, gamma: float, epsilon: float) -> None:
        self.model = model
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.optimizer = optim.Adam(model.parameters(), lr=self.learning_rate, weight_decay=0.001)
        self.criterion = nn.MSELoss()
        self.epsilon = epsilon
        self.epoch = 0

    def save(self, id: int, games: int, gap: int) -> None:
        self.epoch = int(games / gap)
        display_eps = int(round(self.epsilon, 3) * 1000)
        if display_eps == 0:
            display_eps = "000"
        elif display_eps < 10:
            display_eps = "00" + str(display_eps)
        elif display_eps < 100:
            display_eps = "0" + str(display_eps)
        # path = f'./model/checkpoint_epo{self.epoch}_eps{display_eps}.pth'
        path = f'./model/agent{id}/checkpoint_epo{self.epoch}_eps{display_eps}.pth'

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

    def update_epsilon(self, decay: float) -> None:
        self.epsilon *= decay

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

class LinearTrainer(Trainer):
    def __init__(self, model: nn.Module, learning_rate: float, gamma: float, epsilon: float) -> None:
        super(LinearTrainer, self).__init__(model, learning_rate, gamma, epsilon)

        self.previous_state = None
        self.previous_next_state = None
        self.previous_mask = None
        self.previous_action = None

        self.batch_size = 1000
        self.memory = []

    def memorise(self, state: np.ndarray, action: int, reward: int, next_state: np.ndarray, hand: list[int]) -> None:
        state = torch.tensor(state, dtype=torch.float)
        action = torch.tensor([action], dtype=torch.int)
        reward = torch.tensor([reward], dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)

        available_cards = [h for h in hand]
        available_cards = torch.tensor(available_cards, dtype=torch.long)

        mask = torch.zeros(self.model.output_size)
        mask[available_cards] = 1

        if action == -1:
            self.memory.append([self.previous_state, self.previous_action, reward, self.previous_next_state, self.previous_mask])
        else:
            self.memory.append([state, action, reward, next_state, mask])

        self.previous_state = state.clone()
        self.previous_next_state = next_state.clone()
        self.previous_mask = mask.clone()
        self.previous_action = action.item()

    def train_er(self) -> None:
        # experience relay buffer, sample memory as buffer
        batch = random.sample(self.memory, self.batch_size)

        states = torch.stack([experience[0] for experience in batch])
        actions = torch.tensor([experience[1] for experience in batch])
        rewards = torch.tensor([experience[2] for experience in batch])
        next_states = torch.stack([experience[3] for experience in batch])
        masks = torch.stack([experience[4] for experience in batch])

        Q_value = self.model(states)

        # Normalize Q-values using min-max normalization
        q_min = torch.min(Q_value)
        q_max = torch.max(Q_value)
        Q_value = (Q_value - q_min) / (q_max - q_min)

        # make unavailable actions 0 for loss calculation
        Q_value = Q_value * masks

        # print(self.model(next_state))
        Q_new_value = rewards + self.gamma * torch.max(self.model(next_states) * masks)
        target = Q_value.clone()

        # action_mask has boolean values to map the Q_new_values in the right indices of the batch
        actions_mask = torch.zeros_like(target, dtype=torch.bool)
        actions_mask[torch.arange(len(actions)), actions] = True

        target[actions_mask] = Q_new_value

        self.optimizer.zero_grad()
        loss = self.criterion(target, Q_value)
        loss.backward()
        # print(loss.item())
        self.optimizer.step()

    def train(self, state: np.ndarray, action: int, reward: int, next_state: np.ndarray, hand: list[int]) -> None:
        state = torch.tensor(state, dtype=torch.float)
        action = torch.tensor([action], dtype=torch.int)
        reward = torch.tensor([reward], dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)

        available_cards = [h for h in hand]
        available_cards = torch.tensor(available_cards, dtype=torch.long)
        print(hand)

        mask = torch.zeros(self.model.output_size)
        mask[available_cards] = 1

        # no op
        if action.item() == -1:
            Q_value = self.model(self.previous_state)

            # Normalize Q-values using min-max normalization
            q_min = torch.min(Q_value)
            q_max = torch.max(Q_value)
            Q_value = (Q_value - q_min) / (q_max - q_min)

            # make unavailable actions 0 for loss calculation
            Q_value = Q_value * self.previous_mask

            # print(self.model(next_state))
            Q_new_value = reward + self.gamma * torch.max(self.model(self.previous_next_state) * self.previous_mask)
            target = Q_value.clone()

            target[self.previous_action] = Q_new_value
        else:
            Q_value = self.model(state)

            # Normalize Q-values using min-max normalization
            q_min = torch.min(Q_value)
            q_max = torch.max(Q_value)
            Q_value = (Q_value - q_min) / (q_max - q_min)

            # make unavailable actions 0 for loss calculation
            Q_value = Q_value * mask

            # print(self.model(next_state))
            Q_new_value = reward + self.gamma * torch.max(self.model(next_state) * mask)
            target = Q_value.clone()

            target[action.item()] = Q_new_value

        # print(Q_value, Q_new_value)
        # print(state)
        # print(next_state)
        # print(available_cards)
        # print(action.item())

        self.optimizer.zero_grad()
        loss = self.criterion(target, Q_value)
        loss.backward()
        # print(loss.item())
        self.optimizer.step()

        self.previous_state = state.clone()
        self.previous_next_state = next_state.clone()
        self.previous_mask = mask.clone()
        self.previous_action = action.item()

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

            # make them infinite instead of 0 because it uses argmax to calculate
            Q_value = torch.where(mask == 1, Q_value, torch.tensor(float('-inf'), device=Q_value.device))

            # print(hand)
            # print(mask)
            # print(Q_value)
            # print(torch.argmax(Q_value).item() + 1)

            res = torch.argmax(Q_value).item() + 1
            return hand.index(res)

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
        self.rnn = nn.GRU(input_size, hidden_size, batch_first=True)                # remembers the previous turn cards and deck etc, so dependencies between each turn is tracked compared to LinearQNetwork
        self.linear1 = nn.Linear(hidden_size, hidden_size)                          # linear hidden layer
        self.linear2 = nn.Linear(hidden_size, output_size)                          # linear here to map to output

        self.output_size = output_size

    def forward(self, x: Tensor, h: Tensor) -> Tensor:
        out, h = self.rnn(x, h)
        out = F.relu(self.linear1(out[:, -1]))
        out = self.linear2(out)
        return out, h

class RNNTrainer(Trainer):
    def __init__(self, model: nn.Module, learning_rate: float, gamma: float, epsilon: float) -> None:
        super(RNNTrainer, self).__init__(model, learning_rate, gamma, epsilon)
        self.hidden_state = None

        self.previous_state = None
        self.previous_next_state = None
        self.previous_mask = None
        self.previous_action = None

        self.batch_size = 1000
        self.memory = []

    def memorise(self, state: np.ndarray, action: int, reward: int, next_state: np.ndarray, hand: list[int]) -> None:
        state = torch.tensor(state, dtype=torch.float)
        action = torch.tensor([action], dtype=torch.int)
        reward = torch.tensor([reward], dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)

        available_cards = [h for h in hand]
        available_cards = torch.tensor(available_cards, dtype=torch.long)

        mask = torch.zeros(self.model.output_size)
        mask[available_cards] = 1

        if self.hidden_state is None:
            self.hidden_state = torch.zeros((1, self.batch_size, self.model.hidden_size))       # batch first doesn't affect hidden state I guess

        if action == -1:
            self.memory.append([self.previous_state, self.previous_action, reward, self.previous_next_state, self.previous_mask])
        else:
            self.memory.append([state, action, reward, next_state, mask])

        self.hidden_state = self.hidden_state.detach()

        self.previous_state = state.clone()
        self.previous_next_state = next_state.clone()
        self.previous_mask = mask.clone()
        self.previous_action = action.item()

    def train_er(self) -> None:
        # experience relay buffer, sample memory as buffer
        batch = random.sample(self.memory, self.batch_size)

        states = torch.stack([experience[0] for experience in batch])
        actions = torch.tensor([experience[1] for experience in batch])
        rewards = torch.tensor([experience[2] for experience in batch])
        next_states = torch.stack([experience[3] for experience in batch])
        masks = torch.stack([experience[4] for experience in batch])

        Q_value, self.hidden_state = self.model(states, self.hidden_state)

        # Normalize Q-values using min-max normalization
        q_min = torch.min(Q_value)
        q_max = torch.max(Q_value)
        Q_value = (Q_value - q_min) / (q_max - q_min)

        # make unavailable actions 0 for loss calculation
        Q_value = Q_value * masks

        # print(self.model(next_states))
        Q_new_value, _ = self.model(next_states, self.hidden_state)
        Q_new_value = rewards + self.gamma * torch.max(Q_new_value * masks)
        target = Q_value.clone()

        # action_mask has boolean values to map the Q_new_values in the right indices of the batch
        actions_mask = torch.zeros_like(target, dtype=torch.bool)
        actions_mask[torch.arange(len(actions)), actions] = True

        target[actions_mask] = Q_new_value

        self.optimizer.zero_grad()
        loss = self.criterion(target, Q_value)
        loss.backward()
        # print(loss.item())
        self.optimizer.step()

    def train(self, state: np.ndarray, action: int, reward: int, next_state: np.ndarray, hand: list[int]) -> None:
        state = torch.tensor(state, dtype=torch.float)
        action = torch.tensor([action], dtype=torch.int)
        reward = torch.tensor([reward], dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)

        available_cards = [h for h in hand]
        available_cards = torch.tensor(available_cards, dtype=torch.long)

        mask = torch.zeros(self.model.output_size)
        mask[available_cards] = 1

        if self.hidden_state is None:
            self.hidden_state = torch.zeros((1, self.model.hidden_size))

        # no op
        if action.item() == -1:
            Q_value, self.hidden_state = self.model(self.previous_state, self.hidden_state)

            # Normalize Q-values using min-max normalization
            q_min = torch.min(Q_value)
            q_max = torch.max(Q_value)
            Q_value = (Q_value - q_min) / (q_max - q_min)

            # make unavailable actions 0 for loss calculation
            Q_value = Q_value * self.previous_mask

            # print(self.model(next_state))
            Q_new_value, _ = self.model(self.previous_next_state, self.hidden_state)
            Q_new_value = reward + self.gamma * torch.max(Q_new_value * self.previous_mask)
            target = Q_value.clone()

            target[self.previous_action] = Q_new_value
        else:
            Q_value, self.hidden_state = self.model(state, self.hidden_state)

            # Normalize Q-values using min-max normalization
            q_min = torch.min(Q_value)
            q_max = torch.max(Q_value)
            Q_value = (Q_value - q_min) / (q_max - q_min)

            # make unavailable actions 0 for loss calculation
            Q_value = Q_value * mask

            # print(self.model(next_state))
            Q_new_value, _ = self.model(next_state, self.hidden_state)
            Q_new_value = reward + self.gamma * torch.max(Q_new_value * mask)
            target = Q_value.clone()

            target[action.item()] = Q_new_value

        # print(Q_value, Q_new_value)
        # print(state)
        # print(next_state)
        # print(available_cards)
        # print(action.item())

        self.optimizer.zero_grad()
        loss = self.criterion(target, Q_value)
        loss.backward()
        # print(loss.item())
        self.optimizer.step()

        self.hidden_state = self.hidden_state.detach()

        self.previous_state = state.clone()
        self.previous_next_state = next_state.clone()
        self.previous_mask = mask.clone()
        self.previous_action = action.item()

    def predict(self, state: np.ndarray, hand: list[int]) -> int:
        if random.random() < self.epsilon:
            return int(random.random() * 4)
        else:
            available_cards = [h-1 for h in hand]
            # chooses between all the cards in deck, then picks the best move given on whats on hand
            state = torch.tensor(state, dtype=torch.float)
            available_cards = torch.tensor(available_cards, dtype=torch.long)

            Q_value, _ = self.model(state.unsqueeze(0), torch.zeros((1, 1, self.model.hidden_size)))

            mask = torch.zeros_like(Q_value[0])
            mask[available_cards] = 1

            # make them infinite instead of 0 because it uses argmax to calculate
            Q_value = torch.where(mask == 1, Q_value, torch.tensor(float('-inf'), device=Q_value.device))

            # print(hand)
            # print(mask)
            # print(Q_value)
            # print(torch.argmax(Q_value).item() + 1)

            res = torch.argmax(Q_value).item() + 1
            return hand.index(res)