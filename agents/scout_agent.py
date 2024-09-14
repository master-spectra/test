from agents.base_agent import BaseAgent
from models.reinforcement_learning import PPOAgent

class ScoutAgent(BaseAgent):
    def __init__(self, state_size, action_size):
        super().__init__(state_size, action_size)
        self.model = PPOAgent(state_size, action_size)
        self.explored_areas = set()

    def act(self, state):
        action = self.model.act(state)
        # Приоритет на движение и исследование
        if action in [0, 1, 2, 3]:  # move_forward, move_backward, turn_left, turn_right
            return action
        return self.model.act(state)  # Если не движение, выбираем новое действие

    def train(self, states, actions, rewards, next_states, dones):
        self.model.train(states, actions, rewards, next_states, dones)

    def get_reward(self, game_state):
        reward = 0
        # Награда за исследование новых областей
        current_position = tuple(game_state.robot_positions[0])
        if current_position not in self.explored_areas:
            reward += 10
            self.explored_areas.add(current_position)
        # Награда за обнаружение ресурсов
        for resource in game_state.resources:
            if self.distance(game_state.robot_positions[0], resource) < 5:
                reward += 5
        return reward

    @staticmethod
    def distance(pos1, pos2):
        return ((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2 + (pos1.z - pos2.z)**2)**0.5
