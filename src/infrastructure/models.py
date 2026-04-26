"""
Модуль реализации моделей (Infrastructure) слоя.
Этот слой содержит конкретные реализации интерфейсов, определенных в слое Domain.
Здесь находится код, который взаимодействует с внешними библиотеками (например,
TensorFlow, PyTorch, Scikit-learn) или имитирует их работу (Mock).
"""
import numpy as np
import onnxruntime as ort
from src.domain.interfaces import ISentimentAnalyzer
from src.domain.entities import Review, SentimentScore

class SimpleAnalyzer(ISentimentAnalyzer):
    """
    Заглушка (Mock) модели машинного обучения.
    Используется для разработки и тестирования бизнес-логики (Application Layer)
    без необходимости загружать тяжелые веса реальных нейросетей.
    Реализует интерфейс ISentimentAnalyzer, определенный в Домене.

      Логика работы:
    - Если длина текста > 50 символов: возвращает "Positive"
    - Если длина текста <= 50 символов: возвращает "Negative"
    - Confidence (уверенность) вычисляется на основе длины текста
    """
    def analyze(self, data: Review)-> SentimentScore:
        """
        Реализация метода предсказания.
        Вместо реального инференса возвращает детерминированный ответ,
        основанный на входных данных.
        """
        # Получаем текст из входных данных
        text = data.text
        text_length = len(text)

        # Определяем тональность на основе длины текста
        if text_length > 50:
            sentiment = "Positive"
            # Для длинных текстов уверенность выше
            confidence = min(0.95, 0.7 + (text_length - 50) / 200)
        else:
            sentiment = "Negative"
            # Для коротких текстов уверенность тоже зависит от длины
            confidence = min(0.9, 0.5 + text_length / 100)

        # Формируем результат
        return SentimentScore(
            label=sentiment,
            score=confidence
        )


class ONNXSentimentAnalyzer(ISentimentAnalyzer):
    """
    Реализация анализатора тональности, использующая ONNX модель
    """

    def __init__(self, model_path: str):
        try:
            self.session = ort.InferenceSession(model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load ONNX model: {e}")

        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [o.name for o in self.session.get_outputs()]

    def analyze(self, review: Review) -> SentimentScore:
        text = review.text

        input_data = np.array([[text]], dtype=object)

        outputs = self.session.run(None, {self.input_name: input_data})

        label = outputs[0][0]
        score = 0.9

        return SentimentScore(label=str(label), score=score)