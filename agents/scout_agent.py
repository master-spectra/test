from agents.base_agent import BaseAgent
from models.reinforcement_learning import PPOAgent
from collections import namedtuple

Position = namedtuple('Position', ['x', 'y', 'z'])

class ScoutAgent(BaseAgent):
    def __init__(self, state_size, action_size):
        actions = ["move_forward", "call_for_help", "use_special_ability", "move_backward"]
        super().__init__(state_size, action_size, actions)
        self.model = PPOAgent(state_size, action_size)

    def act(self, state):
        action = self.model.act(state)
        if self.is_unexplored_area_nearby(state):
            return self.actions.index("move_forward")
        elif self.is_enemy_detected(state):
            return self.actions.index("call_for_help")
        elif self.is_resource_detected(state):
            return self.actions.index("use_special_ability")  # Предполагаем, что это маркировка ресурсов
        elif self.is_in_danger(state):
            return self.actions.index("move_backward")
        else:
            return action

    def is_unexplored_area_nearby(self, state):
        robot_position = state.robot_positions[0]
        explored_positions = state.robot_positions + state.enemy_positions + state.resources + state.obstacles
        unexplored_distance = 15.0  # Определяем "неисследованную область" как область в радиусе 15 единиц без известных объектов

        for x in range(int(robot_position.x - unexplored_distance), int(robot_position.x + unexplored_distance), 5):
            for y in range(int(robot_position.y - unexplored_distance), int(robot_position.y + unexplored_distance), 5):
                potential_position = Position(x, y, robot_position.z)
                if all(self.distance(potential_position, pos) > 5 for pos in explored_positions):
                    return True
        return False

    def is_enemy_detected(self, state):
        robot_position = state.robot_positions[0]
        enemy_positions = state.enemy_positions
        detection_range = 20.0  # Разведчик может обнаружить врага на расстоянии до 20 единиц

        for enemy_position in enemy_positions:
            if self.distance(robot_position, enemy_position) < detection_range:
                return True
        return False

    def is_resource_detected(self, state):
        robot_position = state.robot_positions[0]
        resources = state.resources
        detection_range = 15.0  # Разведчик может обнаружить ресурсы на расстоянии до 15 единиц

        for resource_position in resources:
            if self.distance(robot_position, resource_position) < detection_range:
                return True
        return False

    def is_in_danger(self, state):
        robot_position = state.robot_positions[0]
        enemy_positions = state.enemy_positions
        danger_distance = 10.0  # Считаем, что разведчик в опасности, если враг ближе 10 единиц

        for enemy_position in enemy_positions:
            if self.distance(robot_position, enemy_position) < danger_distance:
                return True
        return False
