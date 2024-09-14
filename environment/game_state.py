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
            [self.encode_weather(self.weather)]
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
