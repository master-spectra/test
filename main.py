import asyncio

from training.trainer import Trainer
from utils.unreal_interface import UnrealInterface


async def main():
    unreal_interface = UnrealInterface()
    unreal_interface.start()

    trainer = Trainer(unreal_interface)

    num_episodes = 1000
    max_steps_per_episode = 500

    for episode in range(num_episodes):
        print(f"Starting episode {episode + 1}")
        await trainer.train_episode(max_steps_per_episode)
        print(f"Finished episode {episode + 1}")

    unreal_interface.stop()

if __name__ == "__main__":
    asyncio.run(main())
