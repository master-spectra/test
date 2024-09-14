import unreal
import numpy as np
import random

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
        game_state['visibility'] = UnrealInterface._get_visibility()
        game_state['weather'] = UnrealInterface._get_weather()
        game_state['strategic_points'] = UnrealInterface._get_strategic_points()
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
            damage = UnrealInterface._calculate_damage(actor)
            actor.attack(damage)
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
    def _get_visibility():
        # Реализация тумана войны
        world = unreal.EditorLevelLibrary.get_editor_world()
        fog_density = world.fog_density
        return max(0, 1 - fog_density)

    @staticmethod
    def _get_weather():
        world = unreal.EditorLevelLibrary.get_editor_world()
        return world.current_weather

    @staticmethod
    def _get_strategic_points():
        return UnrealInterface._get_actor_positions('StrategicPoint')

    @staticmethod
    def _calculate_damage(actor):
        base_damage = actor.base_damage
        random_factor = random.uniform(0.8, 1.2)
        return base_damage * random_factor

    @staticmethod
    def heal_robot(actor):
        if actor.can_heal:
            heal_amount = min(10, 100 - actor.health)
            actor.health += heal_amount
            actor.can_heal = False
            unreal.TimerHandle.set_timer(actor, "reset_heal_cooldown", 30.0, False)

    @staticmethod
    def apply_weather_effects(actor):
        weather = UnrealInterface._get_weather()
        if weather == "Rainy":
            actor.movement_speed *= 0.8
        elif weather == "Foggy":
            actor.visibility_range *= 0.6
        elif weather == "Stormy":
            actor.attack_accuracy *= 0.7

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
