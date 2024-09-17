import json
from threading import Thread

import numpy as np
import zmq

from environment.action_space import ActionSpace
from environment.game_state import GameState
from models.reinforcement_learning import PPOAgent


class UnrealInterface:
    def __init__(self, host='localhost', port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.bind(f"tcp://{host}:{port}")
        self.running = False
        self.listening_thread = None
        self.agents = {}
        self.action_space = ActionSpace()
        self.game_state = GameState()

    def start(self):
        self.running = True
        self.listening_thread = Thread(target=self.listen_for_messages)
        self.listening_thread.start()

    def stop(self):
        self.running = False
        if self.listening_thread:
            self.listening_thread.join()
        self.socket.close()
        self.context.term()

    def listen_for_messages(self):
        while self.running:
            try:
                message = self.socket.recv_json()
                self.handle_message(message)
            except zmq.ZMQError:
                if self.running:
                    print("Error in listening thread")
                break

    def handle_message(self, message):
        if message['command'] == 'get_action':
            action = self.get_ai_action(message['data']['agent_id'], message['data']['state'])
            self.send_command('action', {'agent_id': message['data']['agent_id'], 'action': action})
        elif message['command'] == 'update_state':
            self.update_game_state(message['data']['agent_id'], message['data']['state'], message['data']['reward'], message['data']['done'])

    def send_command(self, command, data=None):
        message = json.dumps({"command": command, "data": data})
        self.socket.send_json(message)

    def get_ai_action(self, agent_id, state):
        if agent_id not in self.agents:
            self.agents[agent_id] = self.create_agent(agent_id, state)
        return int(self.agents[agent_id].act(np.array(state)))

    def create_agent(self, agent_id, state):
        state_size = len(state)
        action_size = self.action_space.get_action_size()
        return PPOAgent(state_size, action_size)

    def update_game_state(self, agent_id, state, reward, done):
        if agent_id in self.agents:
            self.agents[agent_id].train(
                states=np.array([state]),
                actions=np.array([self.agents[agent_id].last_action]),
                rewards=np.array([reward]),
                next_states=np.array([state]),
                dones=np.array([done])
            )
        self.game_state.update(self.vector_to_game_state(state))

    @staticmethod
    def game_state_to_vector(game_state):
        return np.array([
            game_state.robot_positions,
            game_state.robot_health,
            game_state.enemy_positions,
            game_state.enemy_health,
            game_state.base_health,
            game_state.enemy_base_health,
            game_state.resources,
            game_state.obstacles,
            game_state.time_of_day,
            game_state.weather
        ]).flatten()

    def vector_to_game_state(self, vector):
        # Предполагаем, что порядок элементов в векторе соответствует порядку в game_state_to_vector
        new_state = {}
        start = 0
        for key in ['robot_positions', 'robot_health', 'enemy_positions', 'enemy_health']:
            end = start + len(getattr(self.game_state, key))
            new_state[key] = vector[start:end].tolist()
            start = end
        for key in ['base_health', 'enemy_base_health']:
            new_state[key] = vector[start]
            start += 1
        for key in ['resources', 'obstacles']:
            end = start + len(getattr(self.game_state, key))
            new_state[key] = vector[start:end].tolist()
            start = end
        new_state['time_of_day'] = vector[start]
        new_state['weather'] = vector[start + 1]
        return new_state

if __name__ == "__main__":
    interface = UnrealInterface()
    try:
        interface.start()
        print("Interface started. Press Ctrl+C to stop.")
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping the interface...")
    finally:
        interface.stop()
