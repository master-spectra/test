import asyncio

from models.reinforcement_learning import PPOAgent
from utils.unreal_interface import UnrealInterface


class Trainer:
    def __init__(self, unreal_interface):
        self.unreal_interface = unreal_interface
        self.agents = {}

    async def train_episode(self, max_steps):
        for step in range(max_steps):
            game_state = await self.unreal_interface.get_game_state()

            for agent_id, agent_state in game_state['agents'].items():
                if agent_id not in self.agents:
                    self.agents[agent_id] = PPOAgent(len(agent_state), self.unreal_interface.action_size)

                action = self.agents[agent_id].act(agent_state)
                await self.unreal_interface.perform_action(agent_id, action)

            new_game_state = await self.unreal_interface.get_game_state()
            reward = self.calculate_reward(game_state, new_game_state)
            done = self.check_if_done(new_game_state)

            for agent_id, agent_state in new_game_state['agents'].items():
                if agent_id in self.agents:
                    self.agents[agent_id].train(
                        states=[game_state['agents'][agent_id]],
                        actions=[self.agents[agent_id].last_action],
                        rewards=[reward],
                        next_states=[agent_state],
                        dones=[done]
                    )

            if done:
                break

    def calculate_reward(self, old_state, new_state):
        # Implement reward calculation based on game state changes
        reward = 0
        reward += (new_state['base_health'] - old_state['base_health']) * 0.1
        reward += (old_state['enemy_base_health'] - new_state['enemy_base_health']) * 0.2
        reward += len(new_state['robot_positions']) - len(old_state['robot_positions'])
        return reward

    def check_if_done(self, state):
        return state['base_health'] <= 0 or state['enemy_base_health'] <= 0

async def main():
    unreal_interface = UnrealInterface()
    unreal_interface.start()

    trainer = Trainer(unreal_interface)

    num_episodes = 1000
    max_steps_per_episode = 500

    for episode in range(num_episodes):
        await trainer.train_episode(max_steps_per_episode)

    unreal_interface.stop()

if __name__ == "__main__":
    asyncio.run(main())
