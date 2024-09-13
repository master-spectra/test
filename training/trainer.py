import asyncio
from utils.unreal_interface import UnrealInterface

class Trainer:
    def __init__(self, agents, base_agent, game_state, action_space):
        self.agents = agents
        self.base_agent = base_agent
        self.game_state = game_state
        self.action_space = action_space

    async def train_episode(self, max_steps):
        for step in range(max_steps):
            state = self.game_state.get_state_vector()
            base_state = self.base_agent.get_state(self.game_state)

            # Действие базы
            base_action = self.base_agent.get_action(base_state)
            UnrealInterface.perform_base_action(base_action)

            # Действия роботов
            actions = [agent.act(state) for agent in self.agents]
            for agent, action in zip(self.agents, actions):
                UnrealInterface.perform_action(agent, self.action_space.get_action(action))

            await asyncio.sleep(0.1)

            new_state = UnrealInterface.get_game_state()
            self.game_state.update(new_state)
            next_state = self.game_state.get_state_vector()
            next_base_state = self.base_agent.get_state(self.game_state)

            reward = self.calculate_reward()
            done = self.check_if_done()

            # Обучение базы
            self.base_agent.train(base_state, base_action, reward, next_base_state, done)

            # Обучение роботов
            for agent, action in zip(self.agents, actions):
                agent.remember(state, action, reward, next_state, done)
                agent.train()

            if done:
                break

    def calculate_reward(self):
        # Расчет награды на основе состояния игры
        reward = 0
        reward += (self.game_state.base_health - self.game_state.enemy_base_health) * 0.1
        reward += len(self.game_state.robot_positions) - len(self.game_state.enemy_positions)
        return reward

    def check_if_done(self):
        # Проверка, закончился ли эпизод
        return self.game_state.base_health <= 0 or self.game_state.enemy_base_health <= 0
