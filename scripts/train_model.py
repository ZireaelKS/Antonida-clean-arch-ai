import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import StringTensorType

def train():
    # Данные для обучения (должны совпадать по длине!)
    X = [
        # Positive
        "отлично", "супер", "прекрасно", "замечательно", "Отличный сервис",
        "Очень доволен", "Всё понравилось", "Качественная работа", "Спасибо",
        "Лучший сервис", "Все отлично", "Отличная работа все супер",
        "Мне очень понравилось", "Доволен результатом", "Прекрасная работа",
        "Отличная работа, все супер", "Молодцы", "Класс", "Здорово",
        "Неплохо", "Хорошо", "Нормально",  # Добавили нейтральные/позитивные
        # Negative
        "ужасно", "плохо", "отвратительно", "разочарован", "Ужасный сервис",
        "Ничего не работает", "Плохой опыт", "Не рекомендую", "Отвратительная поддержка",
        "Зря потратил деньги", "Полный отстой", "Разочарован качеством",
        "Хуже некуда", "Ужасная работа", "Все сломалось", "Отстой",
        "Так себе", "Не очень", "Средне",  # Добавили нейтральные/негативные
    ]

    y = [
        "Positive", "Positive", "Positive", "Positive", "Positive",
        "Positive", "Positive", "Positive", "Positive", "Positive",
        "Positive", "Positive", "Positive", "Positive", "Positive",
        "Positive", "Positive", "Positive", "Positive",
        "Positive", "Positive", "Positive",  # Для добавленных позитивных
        "Negative", "Negative", "Negative", "Negative", "Negative",
        "Negative", "Negative", "Negative", "Negative", "Negative",
        "Negative", "Negative", "Negative", "Negative", "Negative", "Negative",
        "Negative", "Negative", "Negative",  # Для добавленных негативных
    ]

    print(f"Обучающая выборка: {len(X)} примеров")
    print(f"Positive: {y.count('Positive')}, Negative: {y.count('Negative')}")

    # Проверка совпадения длин
    assert len(X) == len(y), f"Длины не совпадают: X={len(X)}, y={len(y)}"

    # Обучение
    # pipeline = Pipeline([
    #     ('tfidf', TfidfVectorizer()),
    #     ('clf', LogisticRegression())
    # ])
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_features=1000
        )),
        ('clf', LogisticRegression(
            C=10.0,
            random_state=42,
            max_iter=1000,
            class_weight='balanced'
        ))
    ])

    pipeline.fit(X, y)

    # Оценка качества
    train_score = pipeline.score(X, y)
    print(f"Точность на обучении: {train_score:.4f}")

    # Тестовые предсказания
    test_reviews = [
        "Отличная работа, все супер!",
        "Ужасно, ничего не получилось",
        "Нормально, но есть вопросы",
        "Хотелось бы лучшего, но так хорошо",
        "Нормально"
    ]

    print("\nТестовые предсказания:")
    for review in test_reviews:
        pred = pipeline.predict([review])[0]
        prob = pipeline.predict_proba([review])[0]
        confidence = max(prob)
        print(f"   '{review[:30]}...' → {pred} (уверенность: {confidence:.3f})")

    # Конвертация в ONNX
    initial_type = [('input_text', StringTensorType([None, 1]))]
    print("\nКонвертация в ONNX формат...")
    onnx_model = convert_sklearn(
        pipeline,
        initial_types=initial_type
    )

    # Сохранение модели
    output_dir = "models"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "sentiment_model.onnx")

    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"   Старый файл удален: {output_path}")

    with open(output_path, "wb") as f:
        f.write(onnx_model.SerializeToString())

    print(f"\nМодель успешно сохранена в {output_path}")
    print(f"Размер файла: {os.path.getsize(output_path) / 1024:.2f} KB")

    return pipeline


if __name__ == "__main__":
    train()