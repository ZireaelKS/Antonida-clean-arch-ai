"""
Модуль API (Presentation Layer) на базе FastAPI.
Этот модуль отвечает за обработку HTTP-запросов. Он является точкой входа
для внешних систем (веб-фронтенд, мобильные приложения, другие сервисы).
Здесь происходит преобразование HTTP-запросов в вызовы бизнес-логики (Application Layer).
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from src.presentation.schemas import ReviewRequest
from src.presentation.dependencies import get_review_service, get_sync_service

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

    print("[Startup] Инициализация хранилища и синхронизация данных...")
    try:
        sync_service = get_sync_service()

        sync_service.sync_dataset(
            remote_path="demo/test_invoice.txt",
            local_path="data/docs/invoices/demo_review.txt"
        )

        sync_service.sync_dataset(
            remote_path="sentiment_model.onnx",
            local_path="models/sentiment_model.onnx"
        )

    except Exception as e:
        # Важно: ловим ошибку, чтобы сервер все равно запустился,
        # даже если MinIO недоступен (Graceful Degradation).
        print(f"[Startup Error] Ошибка синхронизации: {e}")

    yield
    # --- 2. Shutdown (Очистка ресурсов) --
    # Здесь можно закрыть соединения с БД или остановить фоновые задачи.
    print("[Shutdown] Остановка сервера...")


app = FastAPI(
    title="Sentiment Analyzer API",
    lifespan=lifespan
)

@app.get("/")
def root():
    """
    Проверка работоспособности API (Health Check).
    Используется системами мониторинга (k8s probes) для проверки статуса сервиса.
    """
    return {"message": "API is running. Go to /docs to test the sentiment analyzer."}


@app.post("/analyze")
def analyze(req: ReviewRequest, service = Depends(get_review_service)):
    return service.analyze(req.text, req.author)