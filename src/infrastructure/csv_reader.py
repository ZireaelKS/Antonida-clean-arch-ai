"""
Модуль для чтения данных из CSV файла.
Реализует чтение отзывов из файла, скачанного из S3/MinIO.
"""
import csv
from typing import List
from pathlib import Path
from src.domain.entities import Review


class CSVReviewReader:
    """
    Читатель CSV файлов с отзывами.
    Преобразует данные из CSV в список доменных сущностей Review.
    """

    def __init__(self, file_path: str):
        """
        Инициализация читателя.

        Args:
            file_path: Путь к CSV файлу
        """
        self.file_path = Path(file_path)

    def read_all(self) -> List[Review]:
        """
        Читает все строки из CSV файла и преобразует в Review.

        Returns:
            List[Review]: Список сущностей Review
        """
        reviews = []

        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                review = Review(
                    text=row.get('text', ''),
                    author=row.get('author', 'Anonymous')
                )
                reviews.append(review)

        return reviews

    def read_by_author(self, author: str) -> List[Review]:
        """
        Читает отзывы конкретного автора.

        Args:
            author: Имя автора

        Returns:
            List[Review]: Список отзывов автора
        """
        all_reviews = self.read_all()
        return [r for r in all_reviews if r.author == author]

    def get_authors(self) -> List[str]:
        """
        Получает список всех авторов.

        Returns:
            List[str]: Список уникальных авторов
        """
        reviews = self.read_all()
        return list(set(r.author for r in reviews))

    def get_statistics(self) -> dict:
        """
        Получает статистику по отзывам.

        Returns:
            dict: Статистика (всего отзывов, уникальных авторов)
        """
        reviews = self.read_all()
        return {
            "total_reviews": len(reviews),
            "unique_authors": len(set(r.author for r in reviews)),
            "file_path": str(self.file_path)
        }