"""
Модуль реализации хранилища данных (Infrastructure).
Этот слой отвечает за взаимодействие с внешними системами (в данном случае - S3-хранилищем).
Он реализует абстрактные интерфейсы, определенные в слое Domain, скрывая детали
использования библиотеки boto3 от остальной части приложения.
"""
import boto3
from pathlib import Path
from src.domain.interfaces import IDataStorage

class S3Storage(IDataStorage):
    """
    Реализация хранилища для S3-совместимых систем (MinIO, AWS S3).

    Этот класс является адаптером: он переводит вызовы методов интерфейса IDataStorage
    в вызовы методов библиотеки boto3.
    """
    def __init__(self, endpoint_url: str, access_key: str, secret_key: str, bucket: str):
        """
        Инициализация клиента Boto3.

        Args:
            endpoint_url (str): URL сервера MinIO (например, http:-/localhost:9000).
            access_key (str): Логин (Access Key ID).
            secret_key (str): Пароль (Secret Access Key).
            bucket (str): Имя бакета, с которым будем работать.
        """
        # Создаем низкоуровневый клиент для работы с S3.
        # endpoint_url критически важен для работы с локальным MinIO,
        # иначе boto3 будет пытаться подключиться к реальному AWS S3.
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.bucket = bucket

    def download_file(self, remote_path: str, local_path: str) -> None:
        """
        Скачивание файла из бакета.
        """
        print(f"[Storage] Скачивание {remote_path} -> {local_path}--.")
        # Метод download_file автоматически обрабатывает потоковую передачу данных
        self.s3.download_file(self.bucket, remote_path, local_path)

    def upload_file(self, local_path: str, remote_path: str) -> None:
        """
        Загрузка локального файла в бакет.
        """
        print(f"[Storage] Загрузка {local_path} -> {remote_path}--.")
        self.s3.upload_file(local_path, self.bucket, remote_path)