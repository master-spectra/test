from agents.base_agent import BaseAgent
from models.reinforcement_learning import PPOAgent

class DefenseTower(BaseAgent):
    def __init__(self, state_size, action_size):
        actions = ["attack", "scan_area", "repair_self"]
        super().__init__(state_size, action_size, actions)
        self.model = PPOAgent(state_size, action_size)

    def act(self, state):
        action = self.model.act(state)
        if self.is_enemy_in_range(state):
            return self.actions.index("attack")
        elif self.needs_repair(state):
            return self.actions.index("repair_self")
        else:
            return self.actions.index("scan_area")

    def is_enemy_in_range(self, state):
        tower_position = state.tower_positions[0]
        enemy_positions = state.enemy_positions
        attack_range = 30.0  # Башня имеет большую дальность атаки

        for enemy_position in enemy_positions:
            if self.distance(tower_position, enemy_position) <= attack_range:
                return True
        return False

    def needs_repair(self, state):
        tower_health = state.tower_health[0]
        repair_threshold = 50  # Башня нуждается в ремонте, если здоровье ниже 50%

        return tower_health < repair_threshold

    def train(self, states, actions, rewards, next_states, dones):
        self.model.train(states, actions, rewards, next_states, dones)

    def get_reward(self, game_state):
        reward = 0
        # Награда за нанесение урона врагу
        reward += (100 - game_state.enemy_base_health) * 0.2
        # Награда за сохранение своего здоровья
        reward += game_state.tower_health[0] * 0.1
        return reward
