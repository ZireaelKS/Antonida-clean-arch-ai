"# Antonida-clean-arch-ai"
Clean Architecture AI - Анализатор тональности отзывов (Вариант №2)

## Описание слоев
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


## Настройка проекта
#### Предварительные требования
Python 3.10+
Poetry (управление зависимостями)
Pydantic: Описание и валидация сущностей (Entities).
FastAPI: Веб-интерфейс API.
Docker: Запуск инфраструктуры (MinIO).
DVC (Data Version Control): Управление версиями данных.
Boto3: Работа с S3-хранилищем (MinIO).
Pytest: Модульное тестирование.

#### Инициализация git-репозитория
```
git init
```

#### Установка и инициализация poetry
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

#### Запуск MinIO через Docker Compose
```
docker-compose up -d
```

#### Создайте бакет (Bucket):
- Откройте браузер и перейдите по адресу: http://localhost:9001.
- Войдите в систему, используя логин и пароль
- В меню слева выберите Buckets → Create Bucket.
- Введите имя бакета: datasets и нажмите Create Bucket.

#### Настройка DVC (Data Version Control)
##### 1. Инициализация DVC
```
poetry run dvc init
```

##### 2. Настройка удаленного хранилища (MinIO)
```
## Добавление удаленного хранилища
poetry run dvc remote add -d minio s3://datasets

## Настройка URL локального MinIO
poetry run dvc remote modify minio endpointurl http://localhost:9000

## Настройка учетных данных
poetry run dvc remote modify minio access_key_id minioadmin
poetry run dvc remote modify minio secret_access_key minioadmin
```

**Важно:** Порты MinIO
- **9000** - API endpoint (для DVC, boto3, AWS CLI)
- **9001** - Web Console (браузерный интерфейс)

DVC работает через API, поэтому используем порт **9000**.


##### 3. Добавление данных под контроль DVC
```
## Добавление целой папки
poetry run dvc add data/docs

## Добавление одного файла
poetry run dvc add data/reviews.csv
```
Добавляйте папки с осторожностью:
- Если папка большая (гигабайты), dvc add может работать долго
- При изменении любого файла в папке, DVC будет считать всю папку изменённой
- Нельзя выборочно восстановить один файл - только всю папку целиком


##### 4. Отправка данных в MinIO
```
poetry run dvc push
```

##### Установка uvicorn
```
poetry add uvicorn
```

##### Установка FastAPI
```
poetry add fastapi
```

## Запуск проекта
#### Запуск через CLI
**С аргументом командной строки**
```
poetry run python -m src.presentation.cli "This movie is fantastic!"
```

**С текстом по умолчанию**
```
poetry run python -m src.presentation.cli
```

**Проверить синхронизацию данных**
```
# Синхронизировать данные из MinIO (принудительно)
poetry run python -m src.presentation.cli --sync
```

**Протестировать анализ CSV файла**
```
# Анализ всех отзывов из CSV
poetry run python -m src.presentation.cli --csv data/reviews.csv
```

Если файл отсутствует локально, то будет выполнена попытка синхронизировать данные из MinIO

**Проверить DVC статус**
```
# Проверить статус данных
poetry run dvc status
```

**Запуск скрипта который автоматически подготовит MinIO для работы приложения**
```
poetry run python scripts/init_minio.py
```

**Запуск сервера API**
```
poetry run uvicorn src.presentation.api:app --reload
```

**Открыть документацию FastAPI**

В браузере откройте: http://localhost:8000/docs

## Запуск тестов
```
poetry run pytest
```

## Конфигурация
```
Параметры подключения к хранилищу можно переопределить через переменные окружения:
MINIO_ENDPOINT
 (default: http://localhost:9000)
MINIO_ACCESS_KEY
 (default: minioadmin)
MINIO_SECRET_KEY
 (default: minioadmin)
MINIO_BUCKET
 (default: datasets)
```