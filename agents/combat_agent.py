from agents.base_agent import BaseAgent
from models.reinforcement_learning import DQNAgent

class CombatAgent(BaseAgent):
    def __init__(self, state_size, action_size):
        super().__init__(state_size, action_size)
        self.model = DQNAgent(state_size, action_size)

    def act(self, state):
        return self.model.act(state)

    def train(self, batch_size):
        self.model.train(batch_size)
