import numpy as np

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

    def update_robot_health(self):
        for i, robot in enumerate(self.robot_positions):
            if self.robot_health[i] > 0:
                enemies_in_range = [enemy for enemy in self.enemy_positions
                                    if self.distance(robot, enemy) < 5.0]
                if not enemies_in_range:
                    # Если рядом нет врагов, восстанавливаем здоровье
                    self.robot_health[i] = min(100, self.robot_health[i] + 5)

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
        weathers = ['clear', 'rainy', 'foggy', 'stormy']
        return weathers.index(weather)

    @staticmethod
    def distance(pos1, pos2):
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)**0.5
