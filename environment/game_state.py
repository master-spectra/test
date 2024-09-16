import numpy as np

from utils.unreal_interface import UnrealInterface


class GameState:
    def __init__(self):
        self.robot_positions = []
        self.robot_health = []
        self.robot_types = []
        self.enemy_positions = []
        self.enemy_health = []
        self.enemy_types = []
        self.base_health = 100
        self.enemy_base_health = 100
        self.obstacles = []
        self.resources = []
        self.base_resources = 1000
        self.terrain = []
        self.time_of_day = 0  # 0-23 часа
        self.weather = "clear"  # clear, rainy, foggy, etc.
        self.tower_positions = []
        self.tower_health = []
        self.covers = []
        self.strategic_points = []
        self.collected_resources = 0
        self.robot_energy = []
        self.visibility = 1.0  # 0.0 - 1.0, где 0.0 - полная темнота, 1.0 - полная видимость
        self.unreal_interface = UnrealInterface()

    def update(self, new_state):
        self.robot_positions = new_state['robot_positions']
        self.robot_health = new_state['robot_health']
        self.robot_types = new_state['robot_types']
        self.enemy_positions = new_state['enemy_positions']
        self.enemy_health = new_state['enemy_health']
        self.enemy_types = new_state['enemy_types']
        self.base_health = new_state['base_health']
        self.enemy_base_health = new_state['enemy_base_health']
        self.obstacles = new_state['obstacles']
        self.resources = new_state['resources']
        self.base_resources = new_state['base_resources']
        self.terrain = new_state['terrain']
        self.time_of_day = new_state['time_of_day']
        self.weather = new_state['weather']
        self.tower_positions = new_state['tower_positions']
        self.tower_health = new_state['tower_health']
        self.covers = new_state['covers']
        self.strategic_points = new_state['strategic_points']
        self.collected_resources = new_state['collected_resources']
        self.robot_energy = new_state['robot_energy']
        self.visibility = new_state['visibility']
        self.update_robot_health()
        self.apply_weather_effects()

    def update_robot_health(self):
        for i, robot in enumerate(self.robot_positions):
            if self.robot_health[i] > 0:
                enemies_in_range = [enemy for enemy in self.enemy_positions
                                    if self.distance(robot, enemy) < 5.0]
                if not enemies_in_range:
                    self.unreal_interface.send_command("heal_robot", {"robot_id": i})

    def apply_weather_effects(self):
        self.unreal_interface.send_command("apply_weather_effects", {"weather": self.weather})

    def get_state_vector(self):
        state = np.concatenate([
            np.array(self.robot_positions).flatten(),
            np.array(self.robot_health),
            np.array([self.encode_robot_type(t) for t in self.robot_types]),
            np.array(self.enemy_positions).flatten(),
            np.array(self.enemy_health),
            np.array([self.encode_robot_type(t) for t in self.enemy_types]),
            [self.base_health, self.enemy_base_health, self.base_resources],
            np.array(self.obstacles).flatten(),
            np.array(self.resources).flatten(),
            np.array(self.terrain).flatten(),
            [self.time_of_day],
            [self.encode_weather(self.weather)],
            np.array(self.tower_positions).flatten(),
            np.array(self.tower_health),
            np.array(self.covers).flatten(),
            np.array(self.strategic_points).flatten(),
            [self.collected_resources],
            np.array(self.robot_energy),
            [self.visibility]
        ])
        return state

    @staticmethod
    def encode_robot_type(robot_type):
        types = ['melee', 'ranged', 'tank', 'scout']
        return types.index(robot_type)

    @staticmethod
    def encode_weather(weather):
        weathers = ['Clear', 'Rainy', 'Foggy', 'Stormy']
        return weathers.index(weather)

    @staticmethod
    def distance(pos1, pos2):
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)**0.5

    def is_game_over(self):
        return self.base_health <= 0 or self.enemy_base_health <= 0

    def get_reward(self):
        reward = 0
        reward += (self.base_health - self.enemy_base_health) * 0.1
        reward += len(self.robot_positions) - len(self.enemy_positions)
        reward += self.collected_resources * 0.01
        return reward

    def add_robot(self, robot_type, position):
        self.robot_positions.append(position)
        self.robot_types.append(robot_type)
        self.robot_health.append(100)  # Начальное здоровье
        self.robot_energy.append(100)  # Начальная энергия

    def remove_robot(self, index):
        del self.robot_positions[index]
        del self.robot_types[index]
        del self.robot_health[index]
        del self.robot_energy[index]

    def update_resource(self, resource_index, new_amount):
        self.resources[resource_index] = new_amount

    def update_visibility(self, new_visibility):
        self.visibility = max(0.0, min(1.0, new_visibility))

    def update_time_of_day(self):
        self.time_of_day = (self.time_of_day + 1) % 24
        # Обновляем видимость в зависимости от времени суток
        if 6 <= self.time_of_day < 18:
            self.visibility = 1.0
        else:
            self.visibility = 0.5
