import pytest
import os


@pytest.fixture(scope="session")
def model_path():
    path = "models/sentiment_model.onnx"

    if not os.path.exists(path):
        pytest.skip("Модель не найдена, пропуск integration тестов")

    return path