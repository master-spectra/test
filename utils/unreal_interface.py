import unreal
import numpy as np

class UnrealInterface:
    @staticmethod
    def get_game_state():
        # Получение состояния игры из Unreal Engine
        game_state = {}
        game_state['robot_positions'] = UnrealInterface._get_actor_positions('Robot')
        game_state['enemy_positions'] = UnrealInterface._get_actor_positions('Enemy')
        game_state['base_health'] = unreal.GameplayStatics.get_actor_of_class(unreal.EditorLevelLibrary.get_editor_world(), unreal.PlayerBase).health
        game_state['enemy_base_health'] = unreal.GameplayStatics.get_actor_of_class(unreal.EditorLevelLibrary.get_editor_world(), unreal.EnemyBase).health
        game_state['obstacles'] = UnrealInterface._get_actor_positions('Obstacle')
        game_state['resources'] = UnrealInterface._get_actor_positions('Resource')
        return game_state

    @staticmethod
    def perform_action(actor, action):
        # Выполнение действия в Unreal Engine
        if action == "move_forward":
            actor.add_movement_input(actor.get_actor_forward(), 1.0, False)
        elif action == "move_backward":
            actor.add_movement_input(actor.get_actor_forward(), -1.0, False)
        elif action == "turn_left":
            actor.add_controller_yaw_input(-1.0)
        elif action == "turn_right":
            actor.add_controller_yaw_input(1.0)
        elif action == "attack":
            actor.attack()
        elif action == "defend":
            actor.defend()
        elif action == "collect_resource":
            actor.collect_resource()
        elif action == "repair_base":
            actor.repair_base()
        elif action == "call_for_help":
            actor.call_for_help()
        elif action == "use_special_ability":
            actor.use_special_ability()

    @staticmethod
    def _get_actor_positions(actor_class):
        actors = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(), getattr(unreal, actor_class))
        return [actor.get_actor_location() for actor in actors]

    @staticmethod
    def perform_base_action(action):
        # Реализация действий базы
        base = unreal.GameplayStatics.get_actor_of_class(unreal.EditorLevelLibrary.get_editor_world(), unreal.PlayerBase)
        if action == 0:
            base.create_melee_robot()
        elif action == 1:
            base.create_ranged_robot()
        elif action == 2:
            base.create_tank_robot()
        elif action == 3:
            base.create_scout_robot()
