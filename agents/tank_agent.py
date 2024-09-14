from agents.base_agent import BaseAgent
from models.reinforcement_learning import PPOAgent

class TankAgent(BaseAgent):
    def __init__(self, state_size, action_size):
        actions = ["defend", "attack", "repair_base", "move_forward"]
        super().__init__(state_size, action_size, actions)
        self.model = PPOAgent(state_size, action_size)

    def act(self, state):
        action = self.model.act(state)
        if self.is_ally_in_danger(state):
            return self.actions.index("defend")
        elif self.is_enemy_close(state):
            return self.actions.index("attack")
        elif self.is_base_damaged(state):
            return self.actions.index("repair_base")
        elif self.is_strategic_point_nearby(state):
            return self.actions.index("move_forward")
        else:
            return action

    def is_ally_in_danger(self, state):
        ally_positions = state.robot_positions[1:]  # Исключаем позицию текущего танка
        enemy_positions = state.enemy_positions
        danger_distance = 8.0  # Считаем союзника в опасности, если враг ближе 8 единиц

        for ally_position in ally_positions:
            for enemy_position in enemy_positions:
                if self.distance(ally_position, enemy_position) < danger_distance:
                    return True
        return False

    def is_enemy_close(self, state):
        tank_position = state.robot_positions[0]
        enemy_positions = state.enemy_positions
        close_distance = 12.0  # Для танка "близко" - это расстояние менее 12 единиц

        for enemy_position in enemy_positions:
            if self.distance(tank_position, enemy_position) < close_distance:
                return True
        return False

    def is_base_damaged(self, state):
        base_health = state.base_health
        damaged_threshold = 70  # Считаем базу поврежденной, если её здоровье ниже 70%

        return base_health < damaged_threshold

    def is_strategic_point_nearby(self, state):
        tank_position = state.robot_positions[0]
        strategic_points = state.resources + [state.base_position]  # Считаем ресурсы и базу стратегическими точками
        nearby_distance = 15.0  # "Поблизости" для танка - это расстояние менее 15 единиц

        for point in strategic_points:
            if self.distance(tank_position, point) < nearby_distance:
                return True
        return False

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
