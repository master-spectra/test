import json
import socket
import struct
from threading import Thread
from typing import Any, Dict, List, Optional

import numpy as np


class UnrealInterface:
    def __init__(self, host: str = 'localhost', port: int = 8000):
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        self.connection: Optional[socket.socket] = None
        self.listening_thread: Optional[Thread] = None
        self.running = False
        self.agents: Dict[int, Any] = {}  # Здесь Any используется вместо PPOAgent, так как мы не импортируем его напрямую

    def start(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f"Waiting for connection on {self.host}:{self.port}...")
        self.connection, address = self.sock.accept()
        print(f"Connected by {address}")
        self.running = True
        self.listening_thread = Thread(target=self.listen_for_messages)
        self.listening_thread.start()

    def stop(self) -> None:
        self.running = False
        if self.connection:
            self.connection.close()
        if self.sock:
            self.sock.close()
        if self.listening_thread:
            self.listening_thread.join()

    def listen_for_messages(self) -> None:
        while self.running:
            try:
                message = self.receive_data()
                if message:
                    self.handle_message(message)
            except Exception as e:
                print(f"Error in listening thread: {e}")
                break

    def handle_message(self, message: Dict[str, Any]) -> None:
        if message['command'] == 'get_action':
            action = self.get_ai_action(message['data']['agent_id'], message['data']['state'])
            self.send_command('action', {'agent_id': message['data']['agent_id'], 'action': action})
        elif message['command'] == 'update_state':
            self.update_game_state(message['data']['agent_id'], message['data']['state'], message['data']['reward'], message['data']['done'])

    def send_game_state(self, game_state: Dict[str, Any]) -> None:
        state_vector = self.game_state_to_vector(game_state)
        self.send_command("update_state", {"state": state_vector.tolist()})

    def get_ai_action(self, agent_id: int, state: List[float]) -> int:
        if agent_id not in self.agents:
            # Создание нового агента должно быть реализовано здесь
            pass
        return int(self.agents[agent_id].act(np.array(state)))  # Явное приведение к int

    def update_game_state(self, agent_id: int, state: List[float], reward: float, done: bool) -> None:
        if agent_id in self.agents:
            self.agents[agent_id].train(
                states=np.array([state]),
                actions=np.array([self.agents[agent_id].last_action]),
                rewards=np.array([reward]),
                next_states=np.array([state]),
                dones=np.array([done])
            )

    def send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> None:
        message = json.dumps({"command": command, "data": data}).encode()
        if self.connection:
            self.connection.sendall(struct.pack('>I', len(message)) + message)
        else:
            print("Error: No connection established")

    def receive_data(self) -> Optional[Dict[str, Any]]:
        if not self.connection:
            return None
        raw_msglen = self.recvall(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        data = self.recvall(msglen)
        if data:
            return json.loads(data.decode())
        return None

    def recvall(self, n: int) -> Optional[bytes]:
        if not self.connection:
            return None
        data = bytearray()
        while len(data) < n:
            packet = self.connection.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    @staticmethod
    def game_state_to_vector(game_state: Dict[str, Any]) -> np.ndarray:
        return np.array([
            game_state['robot_positions'],
            game_state['robot_health'],
            game_state['enemy_positions'],
            game_state['enemy_health'],
            game_state['base_health'],
            game_state['enemy_base_health'],
            game_state['resources'],
            game_state['obstacles'],
            game_state['time_of_day'],
            game_state['weather']
        ]).flatten()

if __name__ == "__main__":
    interface = UnrealInterface()
    try:
        interface.start()
    except KeyboardInterrupt:
        print("Stopping the interface...")
    finally:
        interface.stop()
