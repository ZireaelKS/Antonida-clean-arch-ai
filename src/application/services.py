"""
Модуль сервисов (Services) слоя Application.
Этот слой реализует сценарии использования (Use Cases) системы.
Сервисы отвечают за оркестрацию потока данных: они получают данные из
Presentation слоя, валидируют их через Domain сущности и передают
в Infrastructure через абстрактные интерфейсы.
"""
from pathlib import Path
from typing import List, Optional
from src.domain.interfaces import ISentimentAnalyzer, IReviewReader
from src.domain.entities import Review, SentimentScore
from src.domain.interfaces import IDataStorage

class ReviewProcessingService:
    """
    Сервис (Use Case) для выполнения предсказаний.
    Этот класс инкапсулирует бизнес-логику процесса предсказания.
    Он не знает, какая именно модель используется (Mock или реальная),
    так как работает с абстракцией BaseModel.
    """
    def __init__(self, analyzer: ISentimentAnalyzer, reader: Optional[IReviewReader] = None):
        """
        Инициализация сервиса с внедрением зависимостей.
        Args:
        analyzer (ISentimentAnalyzer): Реализация анализатора тональности
        (Infrastructure), соответствующая интерфейсу.
        reader (IReviewReader): Реализация читателя отзывов (CSV, JSON)
        """
        self.analyzer = analyzer
        self.reader = reader

    def preprocess(self, raw_text: str) -> str:
        """
        Предобработка текста перед подачей в модель.

        Этот метод должен использоваться как для обучения, так и для инференса
        Args:
            raw_text: Сырой текст с возможными лишними пробелами

        Returns:
            str: Очищенный текст, готовый для подачи в модель
        """
        # Удаляем пробелы в начале и конце
        # Заменяем множественные пробелы внутри текста на один пробел
        cleaned_text = ' '.join(raw_text.strip().split())

        return cleaned_text

    def process_review(self, raw_text: str) -> SentimentScore:
        """
        Выполнение бизнес-сценария обработки отзыва.
        1. Очищает текст от лишних пробелов (бизнес-логика)
        2. Преобразует сырые данные в доменную сущность
        3. Передает в модель для анализа тональности

        Args:
        raw_text: Сырой текст отзыва с возможными лишними пробелами

        Returns:
        PredictionResult: Результат анализа тональности
        """
        # Шаг 1: Предобработка текста через отдельный метод preprocess()
        # Это гарантирует одинаковую обработку для обучения и инференса
        cleaned_text = self.preprocess(raw_text)

        # Шаг 2: Создание доменной сущности (валидация данных)
        input_data = Review(text=cleaned_text, author="Antonida")

        # Шаг 3: Вызов анализатора через абстрактный интерфейс
        result = self.analyzer.analyze(input_data)

        return result

    def run(self, raw_content: str)-> SentimentScore:
        """
        Алиас для process_review (для обратной совместимости).
        """
        return self.process_review(raw_content)

    def load_reviews_from_csv(self) -> list[Review]:
        """
        Загружает отзывы из CSV файла.

        Args:
            csv_path: Путь к CSV файлу

        Returns:
            List[Review]: Список отзывов
        """
        if self.reader is None:
            raise ValueError("Reader not initialized. Cannot load reviews from CSV.")

        return self.reader.read_all()

    def analyze_batch(self) -> list[SentimentScore]:
        """
        Анализирует все отзывы из CSV файла.

        Args:
            csv_path: Путь к CSV файлу

        Returns:
            List[SentimentScore]: Список результатов анализа
        """
        if self.reader is None:
            raise ValueError("Reader not initialized. Cannot analyze batch.")

        reviews = self.load_reviews_from_csv()
        results = []

        for review in reviews:
            result = self.process_review(review.text)
            results.append(result)

        return results


class DataSyncService:
    """
    Сервис (Use Case) для синхронизации локальных данных с облаком.

    Этот компонент отвечает за то, чтобы перед началом работы модели
    необходимые данные (веса, датасеты) гарантированно находились на диске.
    Он использует абстракцию IDataStorage, поэтому не знает, откуда именно
    качаются данные (S3, FTP, Google Drive).
    """

    def __init__(self, storage: IDataStorage):
        """
        Инициализация сервиса.

        Args:
            storage (IDataStorage): Объект, реализующий интерфейс хранилища.
                                    Сюда передается конкретная реализация (например, S3Storage),
                                    но сервис работает с ней только через методы интерфейса.
        """
        # Инверсия зависимостей: зависим от интерфейса, а не от реализации
        self.storage = storage

    def sync_dataset(self, remote_path: str, local_path: str, force: bool = False) -> bool:
        """
        Синхронизирует файл, используя DVC (если есть .dvc файл) или прямое скачивание.
        """
        local_file = Path(local_path)

        if local_file.exists() and not force:
            print(f"[Sync] Файл {local_path} уже существует локально.")
            return True

        # Проверяем, есть ли .dvc файл (значит, данные под DVC)
        dvc_file = Path(local_path + '.dvc')
        if not dvc_file.exists():
            dvc_file = local_file.parent / (local_file.name + '.dvc')

        if dvc_file.exists():
            # Используем DVC для скачивания
            print(f"[Sync] Файл под управлением DVC. Использую dvc pull...")
            import subprocess
            try:
                result = subprocess.run(
                    ["poetry", "run", "dvc", "pull", str(dvc_file)],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"[Sync] Файл успешно восстановлен через DVC")
                return local_file.exists()
            except subprocess.CalledProcessError as e:
                print(f"[Sync Error] DVC pull failed: {e.stderr}")
                return False
        else:
            # Прямое скачивание через boto3
            print(f"[Sync] Файл не под DVC. Скачиваю напрямую из MinIO...")
            if not self.storage.file_exists(remote_path):
                print(f"[Sync Error] Файл {remote_path} не найден в хранилище.")
                return False

            try:
                local_file.parent.mkdir(parents=True, exist_ok=True)
                self.storage.download_file(remote_path, local_path)
                print(f"[Sync] Файл {local_path} успешно загружен.")
                return True
            except Exception as e:
                print(f"[Sync Error] Ошибка загрузки: {e}")
                return False