"# Antonida-clean-arch-ai"
Clean Architecture AI - Анализатор тональности отзывов (Вариант №2)

##Описание слоев
1. **Domain (Ядро)** - src/domain/
entities.py: Содержит Pydantic-модели данных:
Review(text: str, author: str) - сущность отзыва пользователя
SentimentScore(label: str, score: float) - результат анализа тональности
interfaces.py: Определяет абстрактный интерфейс ISentimentAnalyzer с методом analyze()

2. **Application (Бизнес-логика)** - src/application/services.py
ReviewProcessingService: Сценарий использования (Use Case)
preprocess(raw_text: str) -> str - очистка текста от лишних пробелов
process_review(raw_text: str) -> SentimentScore - основной метод обработки
prepare_for_training(raw_texts: list) -> list - подготовка данных для обучения

3. **Infrastructure (Инфраструктура)** - src/infrastructure/analyzers.py
SimpleAnalyzer(ISentimentAnalyzer): Заглушка модели машинного обучения
Логика анализа:
если длина текста > 50 символов → "Positive"
иначе → "Negative"
Confidence вычисляется на основе длины текста

4. **Presentation (Представление)** - src/presentation/
cli.py: Интерфейс командной строки
Поддержка аргументов командной строки


##Настройка проекта
####Предварительные требования
Python 3.10+
Poetry (управление зависимостями)

####Инициализация git-репозитория
```
git init
```

####Установка и инициализация poetry
```
pip install poetry
poetry init
```
В результате в папке проекта должен создаться файл pyproject.toml
После изменения в файле pyproject.toml не забудте обновить библиотеки:
```
poetry lock
poetry install
```


##Запуск проекта
####Запуск через CLI
**С аргументом командной строки**
poetry run python -m src.presentation.cli "This movie is fantastic!"

**С текстом по умолчанию**
poetry run python -m src.presentation.cli

## Запуск тестов
poetry run pytest