import numpy as np
import random

class BaseAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = np.zeros((state_size, action_size))
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

    def get_action(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        return np.argmax(self.q_table[state])

    def train(self, state, action, reward, next_state, done):
        target = reward
        if not done:
            target = reward + self.discount_factor * np.amax(self.q_table[next_state])

        self.q_table[state, action] += self.learning_rate * (target - self.q_table[state, action])

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def get_state(self, game_state):
        # Преобразование game_state в индекс состояния
        # Это упрощенный пример, вам нужно будет адаптировать его под вашу конкретную ситуацию
        num_melee = sum(1 for robot in game_state.robot_positions if robot.type == 'melee')
        num_ranged = sum(1 for robot in game_state.robot_positions if robot.type == 'ranged')
        num_tank = sum(1 for robot in game_state.robot_positions if robot.type == 'tank')
        num_scout = sum(1 for robot in game_state.robot_positions if robot.type == 'scout')

        return (num_melee, num_ranged, num_tank, num_scout)
