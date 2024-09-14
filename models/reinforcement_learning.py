import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.optim.adam import Adam

class PPOAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = 0.99
        self.clip_epsilon = 0.2
        self.actor = nn.Sequential(
            nn.Linear(state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_size),
            nn.Softmax(dim=-1)
        )
        self.critic = nn.Sequential(
            nn.Linear(state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        self.optimizer = Adam(list(self.actor.parameters()) + list(self.critic.parameters()), lr=0.001)

    def act(self, state):
        state = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            action_probs = self.actor(state)
        action = torch.multinomial(action_probs, 1).item()
        return action

    def train(self, states, actions, rewards, next_states, dones):
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        # Вычисление преимущества
        values = self.critic(states).squeeze()
        next_values = self.critic(next_states).squeeze()
        advantages = rewards + self.gamma * next_values * (1 - dones) - values

        # Обновление актора
        action_probs = self.actor(states)
        old_action_probs = action_probs.detach()
        ratio = action_probs.gather(1, actions.unsqueeze(1)) / old_action_probs.gather(1, actions.unsqueeze(1))
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * advantages
        actor_loss = -torch.min(surr1, surr2).mean()

        # Обновление критика
        value_loss = nn.MSELoss()(values, rewards + self.gamma * next_values * (1 - dones))

        # Общая потеря
        loss = actor_loss + 0.5 * value_loss

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
