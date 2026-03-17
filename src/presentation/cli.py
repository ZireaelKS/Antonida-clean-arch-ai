"""
Модуль интерфейса командной строки (CLI) слоя Presentation.
Этот слой отвечает за взаимодействие с внешним миром (пользователем).
Его задачи:
1. Принять ввод от пользователя (аргументы командной строки).
2. Собрать приложение (Composition Root): инициализировать инфраструктуру и внедрить её в
бизнес-логику.
3. Запустить сценарий использования (Use Case).
4. Вывести результат в понятном пользователю формате.
"""
import sys
from src.infrastructure.models import SimpleAnalyzer
from src.application.services import ReviewProcessingService
def main():
    """
    Точка входа в приложение.
    Здесь происходит сборка зависимостей (Dependency Injection).
    Слой Presentation знает обо всех остальных слоях, чтобы соединить их вместе.
    """
    # 1. Инициализация инфраструктуры (Composition Root)
    # Здесь выбираем конкретную реализацию модели.
    # В будущем MockModel можно заменить на TensorFlowModel, изменив только эту строчку.
    analyzer = SimpleAnalyzer()
    # 2. Инициализация бизнес-логики (Внедрение зависимостей / Dependency Injection)
    # Сервис получает готовую модель, не зная, как она устроена внутри.
    service = ReviewProcessingService(analyzer=analyzer)
    # 3. Взаимодействие с пользователем
    # Получение данных из внешнего мира (аргументы CLI)
    input_text = "Hello World"
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
    print(f"Running inference on: '{input_text}'")
    # 4. Запуск сценария использования
    result = service.run(input_text)
    # 5. Вывод результата
    print(f"Result: {result.label} (Confidence: {result.score})")
if __name__ == "__main__":
    main()