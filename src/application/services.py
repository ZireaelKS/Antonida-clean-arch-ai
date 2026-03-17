"""
Модуль сервисов (Services) слоя Application.
Этот слой реализует сценарии использования (Use Cases) системы.
Сервисы отвечают за оркестрацию потока данных: они получают данные из
Presentation слоя, валидируют их через Domain сущности и передают
в Infrastructure через абстрактные интерфейсы.
"""
from src.domain.interfaces import ISentimentAnalyzer
from src.domain.entities import Review, SentimentScore
class ReviewProcessingService:
    """
    Сервис (Use Case) для выполнения предсказаний.
    Этот класс инкапсулирует бизнес-логику процесса предсказания.
    Он не знает, какая именно модель используется (Mock или реальная),
    так как работает с абстракцией BaseModel.
    """
    def __init__(self, analyzer: ISentimentAnalyzer):
        """
        Инициализация сервиса с внедрением зависимостей.
        Args:
        analyzer (ISentimentAnalyzer): Реализация анализатора тональности
        (Infrastructure), соответствующая интерфейсу.
        """
        self.analyzer = analyzer

    def preprocess(self, raw_text: str) -> str:
        """
        Предобработка текста перед подачей в модель.

        Этот метод должен использоваться как для обучения, так и для инференса
        Args:
            raw_text: Сырой текст с возможными лишними пробелами

        Returns:
            str: Очищенный текст, готовый для подачи в модель
        """
        # Удаляем пробелы в начале и конце
        # Заменяем множественные пробелы внутри текста на один пробел
        cleaned_text = ' '.join(raw_text.strip().split())

        return cleaned_text

    def process_review(self, raw_text: str) -> SentimentScore:
        """
        Выполнение бизнес-сценария обработки отзыва.
        1. Очищает текст от лишних пробелов (бизнес-логика)
        2. Преобразует сырые данные в доменную сущность
        3. Передает в модель для анализа тональности

        Args:
        raw_text: Сырой текст отзыва с возможными лишними пробелами

        Returns:
        PredictionResult: Результат анализа тональности
        """
        # Шаг 1: Предобработка текста через отдельный метод preprocess()
        # Это гарантирует одинаковую обработку для обучения и инференса
        cleaned_text = self.preprocess(raw_text)

        # Шаг 2: Создание доменной сущности (валидация данных)
        input_data = Review(text=cleaned_text, author="Antonida")

        # Шаг 3: Вызов анализатора через абстрактный интерфейс
        result = self.analyzer.analyze(input_data)

        return result

    def run(self, raw_content: str)-> SentimentScore:
        """
        Алиас для process_review (для обратной совместимости).
        """
        return self.process_review(raw_content)