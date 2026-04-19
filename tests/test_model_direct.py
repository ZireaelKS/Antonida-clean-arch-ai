import onnxruntime as ort
import numpy as np

# Загружаем новую модель
model_path = "models/sentiment_model.onnx"
session = ort.InferenceSession(model_path)

print("=" * 60)
print(f"Модель загружена: {model_path}")
print(f"Входы: {[inp.name for inp in session.get_inputs()]}")
print(f"Выходы: {[out.name for out in session.get_outputs()]}")
print("=" * 60)

# Тестовые тексты с ожидаемыми результатами
test_cases = [
    ("Отличная работа, все супер!", "Positive"),
    ("Все сломалось", "Negative"),
    ("Ужасный сервис, ничего не работает", "Negative"),
    ("Спасибо большое, очень доволен", "Positive"),
    ("Неплохо", "Positive"),
    ("Отстой полный", "Negative"),
    ("Лучший сервис в мире", "Positive"),
    ("Разочарован качеством", "Negative"),
    ("Молодцы, так держать", "Positive"),
    ("Ничего не работает, полный провал", "Negative"),
]

print("\n🧪 Тестирование модели:\n")

correct = 0
for text, expected in test_cases:
    input_data = np.array([[text]], dtype=np.str_)
    results = session.run(None, {session.get_inputs()[0].name: input_data})

    label = results[0][0]
    probs = results[1][0]

    # Извлекаем уверенность для предсказанного класса
    if isinstance(probs, dict):
        confidence = probs.get(label, 0.0)
    else:
        confidence = max(probs) if hasattr(probs, '__iter__') else 0.0

    status = "✅" if label == expected else "❌"
    if label == expected:
        correct += 1

    print(f"{status} Текст: '{text}'")
    print(f"   Ожидалось: {expected}")
    print(f"   Получено: {label}")
    print(f"   Уверенность: {confidence:.4f}")
    print(f"   Вероятности: {probs}")
    print()

# Итоговая статистика
accuracy = correct / len(test_cases)
print("=" * 60)
print(f"📊 Результаты тестирования:")
print(f"   Правильных ответов: {correct}/{len(test_cases)}")
print(f"   Точность: {accuracy:.2%}")
print("=" * 60)

# Дополнительная проверка на граничных случаях
print("\n🔍 Проверка граничных случаев:")

edge_cases = [
    ("", "Unknown"),  # Пустой текст
    ("А", "Positive"),  # Очень короткий
    ("Очень длинный текст " * 50, "Positive"),  # Очень длинный
]

for text, _ in edge_cases:
    if not text:
        print(f"   ⚠️ Пустой текст: пропускаем (модель может дать неопределенный результат)")
        continue

    input_data = np.array([[text]], dtype=np.str_)
    results = session.run(None, {session.get_inputs()[0].name: input_data})
    label = results[0][0]
    probs = results[1][0]

    print(f"   Текст длиной {len(text)} символов → {label}")