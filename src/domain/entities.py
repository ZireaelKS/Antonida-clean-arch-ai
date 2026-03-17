"""
Модуль сущностей (Entities) слоя Domain.
Этот файл содержит Pydantic-модели, описывающие основные структуры данных системы.
Они обеспечивают строгую типизацию и служат единым контрактом для обмена
данными между слоями Application, Infrastructure и Presentation.
"""
from pydantic import BaseModel as PydanticBaseModel
class Review(PydanticBaseModel):
    """
    Сущность (Entity) входных данных.
    Используется для строгой типизации данных, поступающих в систему
    из внешнего мира (Presentation Layer) в бизнес-логику (Application Layer).
    """
    text: str # Сущность текст
    author: str # Сущность автор

class SentimentScore(PydanticBaseModel):
    """
    Сущность (Entity) результата предсказания.
    Определяет единый контракт ответа для всех моделей в системе.
    Позволяет слою Application не зависеть от формата, который возвращает
    конкретная библиотека (TensorFlow, PyTorch и т.д.).
    """
    label: str
    # Интерпретируемый результат (например, класс "Cat" или "Spam")
    score: float # Степень уверенности модели (обычно от 0.0 до 1.0