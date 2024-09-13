from agents.base_agent import BaseAgent
from models.reinforcement_learning import PPOAgent

class RangedAgent(BaseAgent):
    def __init__(self, state_size, action_size):
        super().__init__(state_size, action_size)
        self.model = PPOAgent(state_size, action_size)

    def act(self, state):
        action = self.model.act(state)
        # Приоритет на атаку и держание дистанции
        if action in [4, 1]:  # attack или move_backward
            return action
        return self.model.act(state)  # Если не атака и не отступление, выбираем новое действие

    def train(self, batch_size):
        self.model.train(batch_size)

    def get_reward(self, game_state):
        reward = 0
        # Награда за нанесение урона врагу
        reward += (100 - game_state.enemy_base_health) * 0.1
        # Награда за сохранение дистанции от врага
        closest_enemy = min([self.distance(game_state.robot_positions[0], enemy) for enemy in game_state.enemy_positions])
        optimal_distance = 5  # Предполагаемая оптимальная дистанция
        reward += 10 - abs(closest_enemy - optimal_distance)
        return reward

    @staticmethod
    def distance(pos1, pos2):
        return ((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2 + (pos1.z - pos2.z)**2)**0.5
