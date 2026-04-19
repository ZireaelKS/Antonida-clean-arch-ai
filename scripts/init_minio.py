import boto3
import os
from botocore.exceptions import ClientError



def upload_demo_data():
    """
    Загружает тестовый файл в MinIO для проверки работы DataSyncService.
    """
    # Настройки подключения (совпадают с docker-compose и api.py)
    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "minioadmin")
    )

    # Список бакетов, которые должны существовать в системе:
    # 1. datasets - для хранения сырых данных и датасетов.
    # 2. models - для хранения версионированных ML-моделей (ONNX).
    buckets = [os.getenv("MINIO_BUCKET", "datasets"), "models"]

    # key = "demo/test_invoice.txt"
    # content = "Тестовый счет для проверки синхронизации API. Сумма: 1000 руб."

    print(f"Подключение к MinIO по адресу {s3.meta.endpoint_url}...")

    # print(f"Загрузка файла '{key}' в бакет '{bucket}'--.")
    # s3.put_object(Bucket=bucket, Key=key, Body=content)
    # print("Успешно! Теперь перезапустите API.")

    # Проходим по всем бакетам и создаем их, если они не существуют
    for bucket_name in buckets:
        try:
            # head_bucket - дешевая операция проверки существования и прав доступа
            s3.head_bucket(Bucket=bucket_name)
            print(f"Бакет '{bucket_name}' уже существует.")
        except ClientError:
            # Если бакет не найден (404), создаем его
            print(f"Создание бакета '{bucket_name}'...")
            s3.create_bucket(Bucket=bucket_name)
    # Загрузка демо-данных для проверки работы DataSyncService
    # Это позволяет запустить API сразу после инициализации, не настраивая DVC вручную.
    bucket = buckets[0]
    key = "demo/test_invoice.txt"  # Путь внутри бакета (S3 Key)
    content = "Тестовый счет для проверки синхронизации API. Сумма: 1000 руб."

    print(f"Загрузка файла '{key}' в бакет '{bucket}'...")
    # put_object загружает данные напрямую из строки или байтов
    s3.put_object(Bucket=bucket, Key=key, Body=content)
    print("Инициализация MinIO завершена.")

if __name__ == "__main__":
    upload_demo_data()