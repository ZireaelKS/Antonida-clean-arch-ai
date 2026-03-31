"""
Модуль интерфейса командной строки (CLI) слоя Presentation.
Этот слой отвечает за взаимодействие с внешним миром (пользователем).
Его задачи:
1. Принять ввод от пользователя (аргументы командной строки).
2. Собрать приложение (Composition Root): инициализировать инфраструктуру и внедрить её в
бизнес-логику.
3. Запустить сценарий использования (Use Case).
4. Вывести результат в понятном пользователю формате.
"""
import sys
import os
import argparse
from src.infrastructure.models import SimpleAnalyzer
from src.infrastructure.storage import S3Storage
from src.application.services import ReviewProcessingService, DataSyncService
def main():
    """
    Точка входа в приложение.
    Здесь происходит сборка зависимостей (Dependency Injection).
    Слой Presentation знает обо всех остальных слоях, чтобы соединить их вместе.
    """

    parser = argparse.ArgumentParser(description="Sentiment Analyzer CLI")
    parser.add_argument("text", nargs="?", help="Text to analyze")
    parser.add_argument("--csv", help="Path to CSV file with reviews")
    parser.add_argument("--sync", action="store_true", help="Sync data from MinIO")

    args = parser.parse_args()

    # --- 0. Конфигурация (обычно берется из .env) --
    s3_config = {
        "endpoint_url": os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        "access_key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        "bucket": os.getenv("MINIO_BUCKET", "datasets")
    }
    # --- 1. Инициализация инфраструктуры (Composition Root) --

    # 1.1 Инициализация хранилища
    storage = S3Storage(**s3_config)

    # 1.2 Инициализация модели
    # Здесь выбираем конкретную реализацию модели.
    analyzer = SimpleAnalyzer()

    # --- 2. Инициализация бизнес-логики (Dependency Injection) --
    # 2.1 Сервис синхронизации данных
    sync_service = DataSyncService(storage=storage)

    # 2.2 Сервис маршрутизации документов
    # Сервис получает готовую модель, не зная, как она устроена внутри.
    service = ReviewProcessingService(analyzer=analyzer)

    # --- 3. Подготовка данных (Синхронизация) --
    # Скачиваем файл, необходимый для демонстрации (если его нет локально)
    # Примечание: В MinIO файл должен лежать по пути 'demo/test_invoice.txt'
    if args.sync:
        print("Синхронизация данных с MinIO...")
        try:
            sync_service.sync_dataset(
                remote_path="reviews.csv",
                local_path="data/reviews.csv"
            )
            print("Данные синхронизированы")
        except Exception as e:
            print(f"Ошибка синхронизации: {e}")

    # --- 4. Запуск ---
    if args.csv:
        # Анализ всех отзывов из CSV
        print(f"Анализ отзывов из файла: {args.csv}")

        # Получаем результаты и сами отзывы
        from src.infrastructure.csv_reader import CSVReviewReader
        reader = CSVReviewReader(args.csv)
        reviews = reader.read_all()

        print(f"\nРезультаты анализа ({len(reviews)} отзывов):")
        print("=" * 60)

        for i, review in enumerate(reviews, 1):
            result = service.process_review(review.text)

            print(f"\n{i}. Отзыв: \"{review.text}\"")
            print(f"  Результат: {result.label} (уверенность: {result.score:.1%})")
    elif args.text:
        # Анализ одного отзыва
        input_text = args.text
        print(f" Текст: \"{input_text}\"")

        result = service.process_review(input_text)
        emoji = ":)" if result.label == "Positive" else ":("

        print(f"\n Результат:")
        print(f"   Тональность: {emoji} {result.label}")
        print(f"   Уверенность: {result.score:.1%}")

    else:
        parser.print_help()

    # ЛАБ №1 (оставлю)
    # #1. Инициализация инфраструктуры (Composition Root)
    # # Здесь выбираем конкретную реализацию модели.
    # # В будущем MockModel можно заменить на TensorFlowModel, изменив только эту строчку.
    # analyzer = SimpleAnalyzer()
    # # 2. Инициализация бизнес-логики (Внедрение зависимостей / Dependency Injection)
    # # Сервис получает готовую модель, не зная, как она устроена внутри.
    # service = ReviewProcessingService(analyzer=analyzer)
    # # 3. Взаимодействие с пользователем
    # # Получение данных из внешнего мира (аргументы CLI)
    # input_text = "Hello World"
    # if len(sys.argv) > 1:
    #     input_text = sys.argv[1]
    # print(f"Running inference on: '{input_text}'")
    # # 4. Запуск сценария использования
    # result = service.run(input_text)
    # # 5. Вывод результата
    # print(f"Result: {result.label} (Confidence: {result.score})")
if __name__ == "__main__":
    main()