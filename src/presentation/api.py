"""
Модуль API (Presentation Layer) на базе FastAPI.
Этот модуль отвечает за обработку HTTP-запросов. Он является точкой входа
для внешних систем (веб-фронтенд, мобильные приложения, другие сервисы).
Здесь происходит преобразование HTTP-запросов в вызовы бизнес-логики (Application Layer).
"""
import os
from contextlib import asynccontextmanager
from functools import lru_cache
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.infrastructure.models import SimpleAnalyzer, ONNXDocumentClassifier
from src.infrastructure.storage import S3Storage
from src.infrastructure.csv_reader import CSVReviewReader
from src.application.services import ReviewProcessingService, DataSyncService
from src.domain.entities import SentimentScore, Review


@lru_cache(maxsize=1)
def get_model():
    """
    Загружает модель в память (Singleton).
    Используется lru_cache, чтобы не создавать объект модели заново на каждый запрос.
    """
    # Путь, куда скачивается модель при старте
    model_path = "models/sentiment_model.onnx"
    print(f"[Model] Загрузка модели из {model_path}...")
    return ONNXDocumentClassifier(model_path)

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

    print("[Startup] Инициализация хранилища и синхронизация данных...")
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

        # --- Синхронизация модели (ЛР №3) ---
        # Создаем конфигурацию для бакета с моделями
        model_s3_config = s3_config.copy()
        model_s3_config["bucket"] = "models"

        model_storage = S3Storage(**model_s3_config)
        model_sync = DataSyncService(storage=model_storage)

        print("[Startup] Проверка наличия обновлений модели в S3...")
        model_sync.sync_dataset(
            remote_path="sentiment_model.onnx",
            local_path="models/sentiment_model.onnx"
        )

        # Предзагрузка модели в память, чтобы первый HTTP-запрос отработал мгновенно
        get_model()
    except Exception as e:
        # Важно: ловим ошибку, чтобы сервер все равно запустился,
        # даже если MinIO недоступен (Graceful Degradation).
        print(f"[Startup Error] Ошибка синхронизации: {e}")

    yield
    # --- 2. Shutdown (Очистка ресурсов) --
    # Здесь можно закрыть соединения с БД или остановить фоновые задачи.
    print("[Shutdown] Остановка сервера...")


app = FastAPI(
    title="Document Classifier API",
    lifespan=lifespan
)

# DTO (Data Transfer Object) для запроса
class ReviewRequest(BaseModel):
    """Модель данных для входящего JSON-запроса."""
    text: str
    author: str = "Antonida"

# DTO (Data Transfer Object) для запроса
class DocumentRequest(BaseModel):
    """Модель данных для входящего JSON-запроса."""
    filename: str
    content: str

# csv_reader = CSVReviewReader("data/reviews.csv")  # Путь к CSV файлу
# analyzer = SimpleAnalyzer()
# review_service = ReviewProcessingService(
#     analyzer=analyzer,
#     reader=csv_reader
# )

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

@app.post("/classify", response_model=SentimentScore)
def classify_document(request: DocumentRequest):
    """
    Эндпоинт для классификации документа.
    Принимает JSON с текстом документа, возвращает категорию и уверенность.
    """
    # 1. Сборка зависимостей (Composition Root)
    # Получаем закэшированный инстанс ONNX-модели
    classifier = get_model()
    # Внедряем модель в бизнес-логику
    # service = DocumentRoutingService(classifier=classifier)
    review = Review(text=request.content, author="System")

    # 2. Вызов Application Layer
    # result = service.run(
    #     filename=request.filename,
    #     raw_content=request.content
    # )
    result = classifier.analyze(review)

    # 3. Возврат результата (FastAPI сам сериализует Pydantic-модель в JSON)
    return result


@app.post("/analyze", response_model=SentimentScore)
def analyze_review(request: ReviewRequest):
    """
    Эндпоинт для анализа тональности одного отзыва.

    Пример запроса:
    {
        "text": "Отличный сервис, очень доволен!",
        "author": "Иван"
    }

    Пример ответа:
    {
        "label": "Positive",
        "score": 0.95
    }
    """
    try:
        classifier = get_model()
        review = Review(text=request.text, author=request.author)
        result = classifier.analyze(review)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")

# Эндпоинт для пакетной обработки
@app.post("/analyze-batch", response_model=list[SentimentScore])
def analyze_batch():
    """
    Эндпоинт для анализа всех отзывов из CSV файла.
    """
    # Создаем сервис прямо здесь, чтобы использовать актуальную модель
    csv_reader = CSVReviewReader("data/reviews.csv")
    analyzer = get_model()  # Используем актуальную модель
    review_service = ReviewProcessingService(analyzer=analyzer, reader=csv_reader)

    results = review_service.analyze_batch()
    return results

