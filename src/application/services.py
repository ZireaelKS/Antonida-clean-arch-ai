"""
Модуль сервисов (Services) слоя Application.
Этот слой реализует сценарии использования (Use Cases) системы.
Сервисы отвечают за оркестрацию потока данных: они получают данные из
Presentation слоя, валидируют их через Domain сущности и передают
в Infrastructure через абстрактные интерфейсы.
"""
from pathlib import Path
from src.domain.interfaces import ISentimentAnalyzer, IDataStorage, IReviewReader
from src.domain.entities import Review, SentimentScore


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

class ReviewProcessingService:
    def __init__(self, analyzer: ISentimentAnalyzer, reader: IReviewReader):
        self.analyzer = analyzer
        self.reader = reader

    def analyze(self, text: str, author: str) -> SentimentScore:
        text = " ".join(text.strip().split())
        review = Review(text=text, author=author)
        return self.analyzer.analyze(review)

    def analyze_batch(self):
        reviews = self.reader.read_all()
        return [self.analyze(r.text, r.author) for r in reviews]