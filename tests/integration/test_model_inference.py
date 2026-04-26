import pytest
import numpy as np
import onnxruntime as ort


@pytest.fixture(scope="session")
def session():
    return ort.InferenceSession("models/sentiment_model.onnx")


@pytest.mark.parametrize("text,expected", [
    ("Отличная работа, все супер!", "Positive"),
    ("Все сломалось", "Negative"),
    ("Ужасный сервис", "Negative"),
])
def test_model_predictions(session, text, expected):

    # ✔ стабильный ONNX input (ВАЖНО)
    input_data = np.array([text], dtype=object).reshape(1, 1)

    input_name = session.get_inputs()[0].name

    outputs = session.run(None, {input_name: input_data})

    label = outputs[0][0]

    assert str(label) == expected