from agents.base_agent import BaseAgent
from models.reinforcement_learning import PPOAgent

class CoverMoverRobot(BaseAgent):
    def __init__(self, state_size, action_size):
        actions = ["move_cover", "move_to_cover", "defend"]
        super().__init__(state_size, action_size, actions)
        self.model = PPOAgent(state_size, action_size)

    def act(self, state):
        action = self.model.act(state)
        if self.is_cover_nearby(state) and self.is_strategic_position(state):
            return self.actions.index("move_cover")
        elif self.is_cover_needed(state):
            return self.actions.index("move_to_cover")
        else:
            return self.actions.index("defend")

    def is_cover_nearby(self, state):
        robot_position = state.robot_positions[0]
        covers = state.covers
        nearby_distance = 5.0

        for cover in covers:
            if self.distance(robot_position, cover) < nearby_distance:
                return True
        return False

    def is_strategic_position(self, state):
        robot_position = state.robot_positions[0]
        strategic_points = state.strategic_points
        strategic_distance = 10.0

        for point in strategic_points:
            if self.distance(robot_position, point) < strategic_distance:
                return True
        return False

    def is_cover_needed(self, state):
        allies = [pos for pos in state.robot_positions if pos != state.robot_positions[0]]
        enemies = state.enemy_positions
        danger_distance = 15.0

        for ally in allies:
            if any(self.distance(ally, enemy) < danger_distance for enemy in enemies):
                return True
        return False

    def train(self, states, actions, rewards, next_states, dones):
        self.model.train(states, actions, rewards, next_states, dones)

    def get_reward(self, game_state):
        reward = 0
        # Награда за перемещение укрытия в стратегическую позицию
        if self.is_cover_nearby(game_state) and self.is_strategic_position(game_state):
            reward += 10
        # Награда за защиту союзников
        if self.is_cover_needed(game_state):
            reward += 5
        return reward
