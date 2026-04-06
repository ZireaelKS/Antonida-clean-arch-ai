"""
Модуль API (Presentation Layer) на базе FastAPI.
Этот модуль отвечает за обработку HTTP-запросов. Он является точкой входа
для внешних систем (веб-фронтенд, мобильные приложения, другие сервисы).
Здесь происходит преобразование HTTP-запросов в вызовы бизнес-логики (Application Layer).
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from src.infrastructure.models import SimpleAnalyzer
from src.infrastructure.storage import S3Storage
from src.infrastructure.csv_reader import CSVReviewReader
from src.application.services import ReviewProcessingService, DataSyncService
from src.domain.entities import SentimentScore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    События жизненного цикла приложения (Lifespan Events).

    Этот менеджер контекста позволяет выполнять код:
    1. При запуске приложения (до начала обработки запросов) - блок до yield.
    2. При остановке приложения - блок после yield.

    Здесь используем это для предварительной загрузки данных из S3,
    чтобы модель не ждала скачивания файлов при первом запросе.
    """
    # --- 1. Startup: Настройка и синхронизация --
    # Считываем конфигурацию подключения к MinIO из переменных окружения.
    # Это позволяет менять настройки без изменения кода (12 Factor App).
    s3_config = {
        "endpoint_url": os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        "access_key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        "bucket": os.getenv("MINIO_BUCKET", "datasets")
    }

    print("[Startup] Инициализация хранилища и синхронизация данных--.")
    try:
        # Инициализируем инфраструктурный слой (S3Storage)
        storage = S3Storage(**s3_config)
        # Внедряем зависимость в сервис синхронизации
        sync_service = DataSyncService(storage=storage)

        # Синхронизируем критически важные данные перед началом работы.
        # Если файлов нет локально, сервер скачает их из MinIO.
        sync_service.sync_dataset(
            remote_path="demo/test_invoice.txt",
            local_path="data/docs/invoices/demo_review.txt"
        )
    except Exception as e:
        # Важно: ловим ошибку, чтобы сервер все равно запустился,
        # даже если MinIO недоступен (Graceful Degradation).
        print(f"[Startup Error] Ошибка синхронизации: {e}")

    yield
    # --- 2. Shutdown (Очистка ресурсов) --
    # Здесь можно закрыть соединения с БД или остановить фоновые задачи.
    print("[Shutdown] Остановка сервера--.")


app = FastAPI(
    title="Document Classifier API",
    lifespan=lifespan
)

# DTO (Data Transfer Object) для запроса
class ReviewRequest(BaseModel):
    """Модель данных для входящего JSON-запроса."""
    text: str
    author: str = "Antonida"

csv_reader = CSVReviewReader("data/reviews.csv")  # Путь к CSV файлу
analyzer = SimpleAnalyzer()
review_service = ReviewProcessingService(
    analyzer=analyzer,
    reader=csv_reader
)

@app.get("/")
def root():
    """
    Проверка работоспособности API (Health Check).
    Используется системами мониторинга (k8s probes) для проверки статуса сервиса.
    """
    return {"message": "API is running. Go to /docs to test the classifier."}

@app.get("/classify")
def classify_info():
    """
    Подсказка, если пользователь случайно открыл этот адрес в браузере (GET-запрос).
    Браузеры по умолчанию делают GET, а наш метод требует POST.
    """
    return {"message": "GET method not allowed. Please use POST request with JSON body to classify documents.Check / docs for details."}


@ app.post("/analyze", response_model=SentimentScore)
def classify_document(request: ReviewRequest):
    """
    Эндпоинт для классификации документа.
    Принимает JSON с текстом документа, возвращает категорию и уверенность.
    """
    # Вызов бизнес-логики
    # передаем данные из DTO (request) в метод сервиса.
    result = review_service.process_review(request.text)

    # Возврат результата
    # FastAPI автоматически сериализует объект SentimentScore (Pydantic модель) в JSON.
    return result

# Эндпоинт для пакетной обработки
@app.post("/analyze-batch", response_model=list[SentimentScore])
def analyze_batch():
    """
    Эндпоинт для анализа всех отзывов из CSV файла.
    """
    results = review_service.analyze_batch()
    return results