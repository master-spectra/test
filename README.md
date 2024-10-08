# Robot Strategy Game AI

Этот проект реализует систему искусственного интеллекта для стратегической игры с роботами, используя методы обучения с подкреплением.

## Описание проекта

Проект включает в себя реализацию ИИ для различных типов роботов (ближнего боя, дальнего боя, танк, разведчик, робот для перемещения укрытий), башен защиты и базы, которая управляет созданием роботов. Система использует алгоритм Proximal Policy Optimization (PPO) для обучения роботов и Q-learning для управления базой.

## Структура проекта

- `main.py`: Главный файл для запуска симуляции
- `environment/`: Определяет игровое состояние и пространство действий
- `agents/`: Содержит классы агентов для различных типов роботов, башен защиты и базы
- `models/`: Реализация нейронных сетей и алгоритмов обучения с подкреплением
- `training/`: Логика обучения агентов
- `utils/`: Вспомогательные функции, включая интерфейс с Unreal Engine
- `tests/`: Модульные тесты
- `cpp_module/`: C++ файлы для интеграции с Unreal Engine

## Основные компоненты

- `PPOAgent`: Реализует алгоритм Proximal Policy Optimization для обучения роботов
- `BaseAgent`: Управляет базой, используя Q-learning для принятия решений о создании роботов
- `GameState`: Представляет текущее состояние игры, включая новые параметры
- `ActionSpace`: Определяет возможные действия для роботов
- `Trainer`: Координирует процесс обучения всех агентов
- `DefenseTower`: Управляет башнями защиты
- `CoverMoverRobot`: Новый тип робота для перемещения укрытий
- `UnrealInterface`: Обеспечивает связь между Python-кодом и Unreal Engine

## Новые функции

- Механика восстановления HP роботов после уничтожения врага
- Улучшенная система наград для более эффективного обучения агентов
- Расширенное состояние игры с дополнительными параметрами

## Установка и запуск

1. Убедитесь, что у вас установлен Python 3.7+
2. Установите необходимые зависимости:
   ```
   pip install torch numpy
   ```
3. Настройте Unreal Engine для работы с Python (см. раздел "Интеграция с Unreal Engine" ниже)
4. Запустите обучение:
   ```
   python main.py
   ```

## Интеграция с Unreal Engine

Для подключения нейронной сети к игре в Unreal Engine, выполните следующие шаги:

1. В вашем проекте Unreal Engine, создайте новую папку `cpp_module` в корневом каталоге.

2. Скопируйте файлы `PythonBridge.h` и `PythonBridge.cpp` из папки `cpp_module` этого проекта в соответствующую папку вашего проекта Unreal Engine.

3. В Unreal Engine, создайте новый C++ класс, наследующийся от AActor, и назовите его PythonBridge.

4. Замените содержимое созданных файлов PythonBridge.h и PythonBridge.cpp содержимым файлов из шага 2.

5. В файле YourProject.Build.cs добавьте "Networking" в PublicDependencyModuleNames:
   ```csharp
   PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "Networking" });
   ```

6. Перекомпилируйте ваш проект Unreal Engine.

7. Создайте Blueprint на основе класса PythonBridge.

8. В вашем уровне или GameMode, добавьте экземпляр PythonBridge и вызовите функцию ConnectToPython() при запуске игры.

9. Используйте функции SendGameState() и GetAIAction() для обмена данными между игрой и ИИ.

Пример использования в Blueprint:

- В событии BeginPlay вашего уровня или GameMode:
  1. Spawn Actor from Class (выберите PythonBridge)
  2. Call Function "ConnectToPython" на созданном акторе

- Для отправки состояния игры:
  1. Создайте массив float для представления состояния игры
  2. Call Function "SendGameState" на акторе PythonBridge, передав этот массив

- Для получения действия от ИИ:
  1. Call Function "GetAIAction" на акторе PythonBridge, передав ID агента
  2. Используйте полученное значение для выполнения действия в игре

## Алгоритм подключения нейронной сети к Unreal Engine 5

1. Подготовка Python-кода:
   - Убедитесь, что ваша нейронная сеть реализована в Python (файл `reinforcement_learning.py`).
   - Проверьте, что класс `PPOAgent` в этом файле имеет методы `act()` и `train()`.

2. Настройка интерфейса Python-Unreal:
   - Используйте существующий файл `unreal_interface.py`.
   - Убедитесь, что в нем есть класс `UnrealInterface` с методами для обмена данными.

3. Создание C++ моста в Unreal Engine:
   - Используйте существующие файлы `PythonBridge.h` и `PythonBridge.cpp`.
   - Убедитесь, что класс `APythonBridge` наследуется от `AActor` и имеет необходимые методы для взаимодействия с Python.

4. Настройка проекта Unreal Engine:
   - В файле `YourProject.Build.cs` добавьте "Networking" в `PublicDependencyModuleNames`.

5. Интеграция в игровой код:
   - В вашем игровом режиме или уровне создайте экземпляр `APythonBridge`.
   - Используйте методы `SendGameState()` и `GetAIAction()` для обмена данными между игрой и ИИ.

6. Запуск и тестирование:
   - Запустите ваш проект в Unreal Engine.
   - Убедитесь, что соединение между Python и Unreal Engine установлено успешно.
   - Проверьте, что игра получает действия от нейронной сети и корректно их обрабатывает.

## Текущее состояние и TODO

- [x] Реализована базовая структура проекта
- [x] Добавлены классы для различных типов роботов
- [x] Реализован PPOAgent для обучения роботов
- [x] Добавлен BaseAgent для управления базой
- [x] Добавлены башни защиты
- [x] Реализован робот для перемещения укрытий
- [x] Улучшена система наград
- [x] Расширено состояние игры
- [x] Добавлен интерфейс для связи с Unreal Engine
- [ ] Провести полное тестирование интеграции с Unreal Engine
- [ ] Оптимизировать гиперпараметры для улучшения обучения
- [ ] Добавить визуализацию процесса обучения
- [ ] Реализовать сохранение и загрузку обученных моделей

## Тестирование

Для запуска модульных тестов используйте команду:
```
python -m unittest discover tests
```

## Вклад в проект

Мы приветствуем вклад в развитие проекта. Пожалуйста, создавайте pull request'ы с вашими улучшениями.

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле LICENSE.
