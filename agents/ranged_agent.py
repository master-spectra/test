from agents.base_agent import BaseAgent
from models.reinforcement_learning import PPOAgent

class RangedAgent(BaseAgent):
    def __init__(self, state_size, action_size):
        actions = ["attack", "move_backward", "use_special_ability", "collect_resource"]
        super().__init__(state_size, action_size, actions)
        self.model = PPOAgent(state_size, action_size)

    def act(self, state):
        action = self.model.act(state)
        if self.is_enemy_in_range(state):
            return self.actions.index("attack")
        elif self.is_enemy_too_close(state):
            return self.actions.index("move_backward")
        elif self.is_ally_under_attack(state):
            return self.actions.index("use_special_ability")  # Предполагаем, что это какая-то поддержка
        elif self.is_resource_nearby(state):
            return self.actions.index("collect_resource")
        else:
            return action

    def is_enemy_in_range(self, state):
        ranged_position = state.robot_positions[0]
        enemy_positions = state.enemy_positions
        attack_range = 20.0  # Дальность атаки для дальнобойного юнита

        for enemy_position in enemy_positions:
            if self.distance(ranged_position, enemy_position) <= attack_range:
                return True
        return False

    def is_enemy_too_close(self, state):
        ranged_position = state.robot_positions[0]
        enemy_positions = state.enemy_positions
        too_close_distance = 5.0  # Считаем врага слишком близко, если он ближе 5 единиц

        for enemy_position in enemy_positions:
            if self.distance(ranged_position, enemy_position) < too_close_distance:
                return True
        return False

    def is_ally_under_attack(self, state):
        ally_positions = state.robot_positions[1:]  # Исключаем позицию текущего дальнобойного юнита
        enemy_positions = state.enemy_positions
        attack_distance = 10.0  # Считаем союзника под атакой, если враг ближе 10 единиц

        for ally_position in ally_positions:
            for enemy_position in enemy_positions:
                if self.distance(ally_position, enemy_position) < attack_distance:
                    return True
        return False

    def is_resource_nearby(self, state):
        ranged_position = state.robot_positions[0]
        resources = state.resources
        nearby_distance = 15.0  # "Поблизости" для дальнобойного юнита - это расстояние менее 15 единиц

        for resource_position in resources:
            if self.distance(ranged_position, resource_position) < nearby_distance:
                return True
        return False

    def train(self, states, actions, rewards, next_states, dones):
        self.model.train(states, actions, rewards, next_states, dones)

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
