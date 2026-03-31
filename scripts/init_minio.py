import boto3
import os
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
    bucket = os.getenv("MINIO_BUCKET", "datasets")
    key = "demo/test_invoice.txt"
    content = "Тестовый счет для проверки синхронизации API. Сумма: 1000 руб."

    print(f"Подключение к MinIO по адресу {s3.meta.endpoint_url}--.")
    print(f"Загрузка файла '{key}' в бакет '{bucket}'--.")
    s3.put_object(Bucket=bucket, Key=key, Body=content)
    print("Успешно! Теперь перезапустите API.")

if __name__ == "__main__":
    upload_demo_data()