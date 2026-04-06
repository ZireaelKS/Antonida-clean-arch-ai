"""
Модуль интерфейсов (Interfaces) слоя Domain.
Этот файл определяет абстрактные базовые классы, которые задают контракт
поведения для компонентов системы. Слой Application зависит от этих интерфейсов,
а слой Infrastructure реализует их (принцип инверсии зависимостей).
"""
from abc import ABC, abstractmethod
from src.domain.entities import Review, SentimentScore
class ISentimentAnalyzer(ABC):
    """
    Абстрактный интерфейс модели ИИ.
    Определяет методы, которые обязана реализовать любая конкретная модель
    (будь то Mock-заглушка, TensorFlow или PyTorch модель) в слое Infrastructure.
    """
    @abstractmethod
    def analyze(self, data: Review)-> SentimentScore:
        """
        Метод для выполнения предсказания.
        Args:
        data (Review): Входные данные в формате сущности домена.
        Returns:
        SentimentScore: Результат предсказания в унифицированном формате.
        """
        pass

class IDataStorage(ABC):
    """
    Абстрактный интерфейс для работы с объектным хранилищем.
    """
    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> None:
        """Скачать файл из облака в локальную файловую систему."""
        pass

    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> None:
        """Загрузить локальный файл в облако."""
        pass


class IReviewReader(ABC):
    """
    Абстрактный интерфейс для чтения отзывов из различных источников данных.
    Определяет контракт для классов, которые читают отзывы (CSV, JSON, БД и т.д.)
    """
    @abstractmethod
    def read_all(self) -> list[Review]:
        """
        Читает все отзывы из источника данных.
        Returns:
            List[Review]: Список сущностей Review
        """
        pass