from agents.base_agent import BaseAgent
from models.reinforcement_learning import PPOAgent  # Изменено здесь

class CombatAgent(BaseAgent):
    def __init__(self, state_size, action_size):
        super().__init__(state_size, action_size)
        self.model = PPOAgent(state_size, action_size)

    def act(self, state):
        return self.model.act(state)

    def train(self, states, actions, rewards, next_states, dones):
        self.model.train(states, actions, rewards, next_states, dones)
