import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from torch.optim.adam import Adam


class PPOAgent:
    def __init__(self, state_size, action_size, learning_rate=3e-4, gamma=0.99, epsilon=0.2, c1=0.5, c2=0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.c1 = c1
        self.c2 = c2

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
        self.optimizer = Adam(list(self.actor.parameters()) + list(self.critic.parameters()), lr=learning_rate)

        self.last_action = None

    def act(self, state):
        state = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            action_probs = self.actor(state)
        dist = Categorical(action_probs)
        action = dist.sample()
        self.last_action = action.item()
        return self.last_action

    def train(self, states, actions, rewards, next_states, dones):
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        # Compute advantages
        with torch.no_grad():
            values = self.critic(states)
            next_values = self.critic(next_states)
            advantages = rewards + self.gamma * next_values * (1 - dones) - values

        # Compute actor loss
        action_probs = self.actor(states)
        dist = Categorical(action_probs)
        new_log_probs = dist.log_prob(actions)
        old_log_probs = new_log_probs.detach()

        ratio = torch.exp(new_log_probs - old_log_probs)
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.epsilon, 1 + self.epsilon) * advantages
        actor_loss = -torch.min(surr1, surr2).mean()

        # Compute critic loss
        value_loss = nn.MSELoss()(self.critic(states), rewards + self.gamma * next_values * (1 - dones))

        # Compute entropy bonus
        entropy = dist.entropy().mean()

        # Total loss
        loss = actor_loss + self.c1 * value_loss - self.c2 * entropy

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()
