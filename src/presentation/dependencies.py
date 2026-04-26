import os
from functools import lru_cache

from src.application.services import (
    ReviewProcessingService,
    DataSyncService
)
from src.infrastructure.models import ONNXSentimentAnalyzer
from src.infrastructure.storage import S3Storage
from src.infrastructure.csv_reader import CSVReviewReader


def get_model():
    model_path = os.getenv("MODEL_PATH", "models/sentiment_model.onnx")
    return ONNXSentimentAnalyzer(model_path)


@lru_cache(maxsize=1)
def get_review_service() -> ReviewProcessingService:
    model = get_model()
    return ReviewProcessingService(analyzer=model,reader=None)

@lru_cache(maxsize=1)
def get_batch_service():
    model = get_model()
    reader = CSVReviewReader("data/reviews.csv")
    return ReviewProcessingService(analyzer=model, reader=reader)

@lru_cache(maxsize=1)
def get_sync_service() -> DataSyncService:
    s3_config = {
        "endpoint_url": os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        "access_key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        "bucket": os.getenv("MINIO_BUCKET", "datasets"),
    }

    storage = S3Storage(**s3_config)
    return DataSyncService(storage=storage)