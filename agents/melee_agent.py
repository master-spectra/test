from agents.base_agent import BaseAgent
from models.reinforcement_learning import PPOAgent

class MeleeAgent(BaseAgent):
    def __init__(self, state_size, action_size):
        actions = ["attack", "move_backward", "move_forward", "collect_resource"]
        super().__init__(state_size, action_size, actions)
        self.model = PPOAgent(state_size, action_size)

    def act(self, state):
        action = self.model.act(state)
        if self.is_enemy_close(state):
            return self.actions.index("attack")
        elif self.health_is_low(state):
            return self.actions.index("move_backward")
        elif self.is_resource_nearby(state):
            return self.actions.index("collect_resource")
        elif self.is_base_under_attack(state):
            return self.actions.index("move_forward")
        else:
            return action

    def is_enemy_close(self, state):
        robot_position = state.robot_positions[0]  # Позиция текущего робота
        enemy_positions = state.enemy_positions
        close_distance = 5.0  # Определяем "близко" как расстояние менее 5 единиц

        for enemy_position in enemy_positions:
            distance = self.distance(robot_position, enemy_position)
            if distance < close_distance:
                return True
        return False

    def health_is_low(self, state):
        robot_health = state.robot_health[0]  # Здоровье текущего робота
        low_health_threshold = 30  # Считаем здоровье низким, если оно меньше 30%

        return robot_health < low_health_threshold

    def is_resource_nearby(self, state):
        robot_position = state.robot_positions[0]
        resources = state.resources
        nearby_distance = 10.0  # Определяем "поблизости" как расстояние менее 10 единиц

        for resource_position in resources:
            distance = self.distance(robot_position, resource_position)
            if distance < nearby_distance:
                return True
        return False

    def is_base_under_attack(self, state):
        base_health = state.base_health
        previous_base_health = getattr(self, 'previous_base_health', 100)  # Предполагаем, что начальное здоровье базы 100

        is_under_attack = base_health < previous_base_health
        self.previous_base_health = base_health  # Сохраняем текущее здоровье базы для следующей проверки

        return is_under_attack

    def train(self, states, actions, rewards, next_states, dones):
        self.model.train(states, actions, rewards, next_states, dones)

    def get_reward(self, game_state):
        reward = 0
        # Награда за нанесение урона врагу
        reward += (100 - game_state.enemy_base_health) * 0.1
        # Награда за близость к врагу
        closest_enemy = min([self.distance(game_state.robot_positions[0], enemy) for enemy in game_state.enemy_positions])
        reward += (1 / closest_enemy) * 10
        return reward

    @staticmethod
    def distance(pos1, pos2):
        return ((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2 + (pos1.z - pos2.z)**2)**0.5
