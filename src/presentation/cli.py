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
import argparse
from src.presentation.dependencies import get_sync_service, get_batch_service, get_review_service


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

    sync_service = get_sync_service()

    # --- 3. Подготовка данных (Синхронизация) --
    # Скачиваем файл, необходимый для демонстрации (если его нет локально)
    # --- Принудительная синхронизация ---
    if args.sync:
        print("Принудительная синхронизация данных с MinIO...")
        if sync_service.sync_dataset("reviews.csv", "data/reviews.csv", force=True):
            print("Данные синхронизированы")
        else:
            print("Ошибка синхронизации")
        return

    # --- Batch режим ---
    if args.csv:
        csv_path = args.csv

        print(f"\n[Batch Mode] Анализ файла: {csv_path}")

        service = get_batch_service()
        results = service.analyze_batch()

        print(f"\nРезультаты ({len(results)}):")
        print("=" * 60)

        for i, result in enumerate(results, 1):
            print(f"{i}. {result.label} ({result.score:.1%})")

        return

    # --- Single текст ---
    if args.text:
        service = get_review_service()
        result = service.analyze(args.text, "CLI")

        print(result)
        return

    parser.print_help()
if __name__ == "__main__":
    main()