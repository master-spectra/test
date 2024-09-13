import numpy as np

class GameState:
    def __init__(self):
        self.robot_positions = []
        self.enemy_positions = []
        self.base_health = 100
        self.enemy_base_health = 100
        self.obstacles = []
        self.resources = []
        self.base_resources = 1000  # Начальные ресурсы базы

    def update(self, new_state):
        self.robot_positions = new_state['robot_positions']
        self.enemy_positions = new_state['enemy_positions']
        self.base_health = new_state['base_health']
        self.enemy_base_health = new_state['enemy_base_health']
        self.obstacles = new_state['obstacles']
        self.resources = new_state['resources']
        self.base_resources = new_state['base_resources']

    def get_state_vector(self):
        state = np.concatenate([
            np.array([[pos.x, pos.y, pos.z, pos.type] for pos in self.robot_positions]).flatten(),
            np.array([[pos.x, pos.y, pos.z] for pos in self.enemy_positions]).flatten(),
            [self.base_health, self.enemy_base_health, self.base_resources],
            np.array([[pos.x, pos.y, pos.z] for pos in self.obstacles]).flatten(),
            np.array([[pos.x, pos.y, pos.z] for pos in self.resources]).flatten()
        ])
        return state
