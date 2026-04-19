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
            label=f"Processed: {sentiment}",
            score=confidence
        )


class ONNXDocumentClassifier(ISentimentAnalyzer):
    """
    Реализация анализатора тональности, использующая ONNX модель
    """

    def __init__(self, model_path: str):
        """
        Инициализация сессии ONNX Runtime.

        Args:
            model_path (str): Путь к файлу модели (.onnx).
        """
        # Загружаем модель и создаем сессию инференса
        self.session = ort.InferenceSession(model_path)

        # Получаем имена входных и выходных узлов графа
        self.input_name = self.session.get_inputs()[0].name
        # Обычно [0] - это label, [1] - probabilities
        self.output_names = [output.name for output in self.session.get_outputs()]


    def analyze(self, data: Review) -> SentimentScore:
        """
        Классификация документа с помощью ONNX модели.
        """
        # Подготовка данных: модель ожидает 2D массив строк [[text]]
        # Согласно скрипту обучения: StringTensorType([None, 1])
        input_data = np.array([[data.text]], dtype=np.str_)
        # Выполнение инференса
        results = self.session.run(self.output_names, {self.input_name: input_data})

        # Обработка результатов
        # ONNX модель возвращает [label, probabilities]
        if len(results) >= 2:
            predicted_label = results[0][0] if isinstance(results[0], (list, np.ndarray)) else results[0]
            probabilities = results[1][0] if len(results) > 1 else {}

            # Извлекаем уверенность для предсказанного класса
            if isinstance(probabilities, dict):
                confidence = probabilities.get(predicted_label, 0.0)
            elif isinstance(probabilities, (list, np.ndarray)):
                confidence = float(max(probabilities))
            else:
                confidence = 0.9
        else:
            predicted_label = results[0][0] if isinstance(results[0], (list, np.ndarray)) else results[0]
            confidence = 0.9

        return SentimentScore(
            label=str(predicted_label),
            score=float(confidence)
        )