import unittest
import torch
import numpy as np

from models.reinforcement_learning import PPOAgent
from environment.game_state import GameState
from environment.action_space import ActionSpace
from agents.base_agent import BaseAgent

class TestPPOAgent(unittest.TestCase):
    def setUp(self):
        self.state_size = 10
        self.action_size = 4
        self.agent = PPOAgent(self.state_size, self.action_size)

    def test_act(self):
        state = np.random.rand(self.state_size)
        action = self.agent.act(state)
        self.assertIsInstance(action, int)
        self.assertTrue(0 <= action < self.action_size)

    def test_train(self):
        states = np.random.rand(5, self.state_size)
        actions = np.random.randint(0, self.action_size, 5)
        rewards = np.random.rand(5)
        next_states = np.random.rand(5, self.state_size)
        dones = np.random.randint(0, 2, 5).astype(float)

        try:
            self.agent.train(states, actions, rewards, next_states, dones)
        except Exception as e:
            self.fail(f"train() вызвал исключение {e}")

class TestGameState(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()

    def test_update(self):
        new_state = {
            'robot_positions': [(0, 0, 0)],
            'robot_health': [100],
            'robot_types': ['melee'],
            'enemy_positions': [(10, 10, 10)],
            'enemy_health': [100],
            'enemy_types': ['ranged'],
            'base_health': 1000,
            'enemy_base_health': 1000,
            'obstacles': [(5, 5, 5)],
            'resources': [(15, 15, 15)],
            'base_resources': 500,
            'terrain': [[0, 1], [1, 0]],
            'time_of_day': 12,
            'weather': 'clear'
        }
        self.game_state.update(new_state)
        self.assertEqual(self.game_state.robot_positions, [(0, 0, 0)])
        self.assertEqual(self.game_state.base_health, 1000)
        self.assertEqual(self.game_state.weather, 'clear')

    def test_get_state_vector(self):
        state_vector = self.game_state.get_state_vector()
        self.assertIsInstance(state_vector, np.ndarray)

class TestActionSpace(unittest.TestCase):
    def setUp(self):
        self.action_space = ActionSpace()

    def test_get_action(self):
        action = self.action_space.get_action(0)
        self.assertEqual(action, "move_forward")

    def test_get_action_size(self):
        size = self.action_space.get_action_size()
        self.assertEqual(size, 10)

class TestBaseAgent(unittest.TestCase):
    def setUp(self):
        self.state_size = 2  # Уменьшим размер состояния для упрощения тестов
        self.action_size = 4
        self.actions = ["create_melee", "create_ranged", "create_tank", "create_scout"]
        self.agent = BaseAgent(self.state_size, self.action_size, self.actions)

    def test_get_action(self):
        state = (1, 1)
        action = self.agent.get_action(state)
        self.assertIsInstance(action, int)
        self.assertTrue(0 <= action < self.action_size)

    def test_train(self):
        state = (1, 1)
        action = 0
        reward = 1.0
        next_state = (0, 1)
        done = False

        try:
            self.agent.train(state, action, reward, next_state, done)
        except Exception as e:
            self.fail(f"train() вызвал исключение {e}")

        state_index = self.agent.state_to_index(state)
        self.assertNotEqual(self.agent.q_table[state_index, action], 0)

if __name__ == '__main__':
    unittest.main()
