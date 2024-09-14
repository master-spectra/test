import asyncio
from environment.game_state import GameState
from environment.action_space import ActionSpace
from agents.melee_agent import MeleeAgent
from agents.ranged_agent import RangedAgent
from agents.tank_agent import TankAgent
from agents.scout_agent import ScoutAgent
from agents.base_agent import BaseAgent
from training.trainer import Trainer
from utils.unreal_interface import UnrealInterface

async def main():
    game_state = GameState()
    action_space = ActionSpace()

    initial_state = UnrealInterface.get_game_state()
    game_state.update(initial_state)

    state_size = len(game_state.get_state_vector())
    action_size = action_space.get_action_size()

    melee_agent = MeleeAgent(state_size, action_size)
    ranged_agent = RangedAgent(state_size, action_size)
    tank_agent = TankAgent(state_size, action_size)
    scout_agent = ScoutAgent(state_size, action_size)

    # Создаем агента базы
    base_state_size = 4  # Количество типов роботов
    base_action_size = 4  # Количество типов роботов, которые может создать база
    base_actions = ["create_melee", "create_ranged", "create_tank", "create_scout"]
    base_agent = BaseAgent(base_state_size, base_action_size, base_actions)

    agents = [melee_agent, ranged_agent, tank_agent, scout_agent]
    trainer = Trainer(agents, base_agent, game_state, action_space)

    num_episodes = 1000
    max_steps_per_episode = 500

    for episode in range(num_episodes):
        await trainer.train_episode(max_steps_per_episode)

if __name__ == "__main__":
    asyncio.run(main())
