from agents.base_agent import BaseAgent
from models.reinforcement_learning import PPOAgent

class TankAgent(BaseAgent):
    def __init__(self, state_size, action_size):
        super().__init__(state_size, action_size)
        self.model = PPOAgent(state_size, action_size)

    def act(self, state):
        action = self.model.act(state)
        # Приоритет на защиту и движение к союзникам
        if action in [5, 0]:  # defend или move_forward
            return action
        return self.model.act(state)  # Если не защита и не движение вперед, выбираем новое действие

    def train(self, states, actions, rewards, next_states, dones):
        self.model.train(states, actions, rewards, next_states, dones)

    def get_reward(self, game_state):
        reward = 0
        # Награда за сохранение здоровья базы
        reward += game_state.base_health * 0.1
        # Награда за близость к союзникам
        allies = [pos for pos in game_state.robot_positions if pos != game_state.robot_positions[0]]
        if allies:
            closest_ally = min([self.distance(game_state.robot_positions[0], ally) for ally in allies])
            reward += (1 / closest_ally) * 10
        return reward

    @staticmethod
    def distance(pos1, pos2):
        return ((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2 + (pos1.z - pos2.z)**2)**0.5
