"""
Модуль модульного тестирования (Unit Testing) слоя Application
Здесь проверяем бизнес-логику изолированно от внешних зависимостей (баз данных,
нейросетей).
Для этого используются Mock-объекты, которые имитируют поведение реальных компонентов.
"""
import pytest
from unittest.mock import Mock
from src.domain.entities import Review, SentimentScore
from src.domain.interfaces import ISentimentAnalyzer
from src.application.services import ReviewProcessingService
def test_prediction_service_logic():
    """
    Тест проверяет корректность работы Use Case (ReviewProcessingService).
    Сценарий:
    1. На вход подается "грязная" строка (с пробелами).
    2. Сервис должен очистить строку.
    3. Сервис должен сформировать правильную сущность InputData.
    4. Сервис должен вызвать модель и вернуть её результат.
    """
    # --- 1. Arrange (Подготовка окружения) --
    # Создаем Mock-объект, который будет притворяться нашей моделью.
    # spec=BaseModel гарантирует, что Mock имеет те же методы, что и интерфейс.
    mock_analyzer = Mock(spec=ISentimentAnalyzer)
    # Настраиваем поведение Mock-а:
    # Когда сервис вызовет метод analyze(), Mock не будет ничего вычислять,
    # а просто вернет заранее подготовленный ответ (Stub).
    expected_result = SentimentScore(label="Positive", score=0.95)
    mock_analyzer.analyze.return_value = expected_result
    # Инициализируем тестируемый сервис, внедряя в него нашу "фейковую" модель.
    # Это и есть Dependency Injection в действии.
    service = ReviewProcessingService(analyzer=mock_analyzer)
    # --- 2. Act (Выполнение действия) --
    # Вызываем метод бизнес-логики с тестовыми данными.
    # Передаем строку с лишними пробелами, чтобы проверить логику предобработки.
    raw_input = "  Hello   AI   World  "
    result = service.run(raw_input)
    # --- 3. Assert (Проверка результатов) --
    # Проверка 1: Сервис вернул именно то, что вернула модель.
    assert result == expected_result
    assert result.label == "Positive"
    assert result.score == 0.95

    # Проверка 2: Сервис действительно обращался к модели.
    mock_analyzer.analyze.assert_called_once()

    # Проверка 3: Валидация данных, переданных в модель.
    # Извлекаем аргументы, с которыми был вызван метод analyze().
    call_args = mock_analyzer.analyze.call_args
    passed_data = call_args[0][0] # args[0] - это первый позиционный аргумент
    # Убеждаемся, что сервис передал данные в формате Domain Entity
    assert isinstance(passed_data, Review)
    # Убеждаемся, что сервис выполнил свою бизнес-задачу: очистил текст от пробелов.
    # Проверяем, что текст был обработан методом preprocess()
    assert passed_data.text == "Hello AI World"  # Используем text вместо content
    assert passed_data.author == "Antonida"  # Проверяем значение по умолчанию
    assert "  " not in passed_data.text  # нет множественных пробелов