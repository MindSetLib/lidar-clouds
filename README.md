# LiDAR Point Cloud Processing Pipeline

Проект реализует полный цикл обработки облака точек LiDAR (PCD) через веб-интерфейс с использованием FastAPI, Celery и моделей детекции.

---

## Функционал

### 1. Загрузка PCD-файла

Пользователь загружает файл `.pcd` через веб-интерфейс фронтенда.

### 2. Приём и постановка задачи

Бэкенд (`lidar_api`) принимает файл, сохраняет его в файловое хранилище и ставит задачу в очередь Celery на обработку.

### 3. Обработка и детекция

Сервис детекции (`lidar_detector`) получает задачу, запускает модель, находит боксы объектов, удаляет ненужные точки и сохраняет итоговый PCD-файл.

### 4. Доступ к результату

Файловое хранилище доступно через nginx. После обработки фронтенд получает файл через `/files/`.

### 5. Статусы обработки

Статусы задач хранятся в Redis. Фронтенд опрашивает бэкенд, пока статус не станет `ready`, после чего отображает результат.

---

## Архитектура

```

Фронтенд (lidar_front)       -> загрузка файла, отображение статуса, просмотр результата
Бэкенд (lidar_api)           -> приём файлов, очередь задач, статусы в Redis, API
Сервис детекции (lidar_detector) -> обработка PCD, запуск модели, сохранение результата
Файловое хранилище           -> общий volume, доступный через nginx
nginx                         -> отдаёт фронтенду фронтенд-статику и готовые файлы
Redis                         -> хранит статусы задач
Celery + брокер               -> очередь задач

```

---

## Структура проекта

```

.
├── docker-compose.yaml          # Настройки контейнеров
├── env_example                  # Пример переменных окружения
├── lidar_api                    # Бэкенд (FastAPI)
├── lidar_detector               # Сервис детекции
├── lidar_front                  # Фронтенд (HTML/JS/TS)
├── ml_services                  # Сервис ML для работы с PCD
├── nginx                        # Конфигурация nginx
├── ocr_configurations           # Конфигурации и утилиты проекта
└── README.md

```

> Все PCD-файлы хранятся в заданной в `.env` DATA\_PATH, проброшенном ко всем сервисам через volume, включая nginx  в `/var/www/lidar_files/`

---

## Nginx конфигурация

- `/api/` → проксирует на `lidar_api:8000`
- `/files/` → отдаёт готовые PCD-файлы из `/var/www/lidar_files/`
- `/` → фронтенд-статика (`index.html`)
- Поддержка CORS и preflight-запросов (`OPTIONS`) для API и статики

Пример nginx.conf:

```nginx
server {
    listen 80;
    server_name _;

    location /api/ {
        proxy_pass http://lidar_api:8000/;
        client_max_body_size 500M;
        add_header 'Access-Control-Allow-Origin' '*' always;
        ...
    }

    location /files/ {
        alias /var/www/lidar_files/;
        autoindex on;
        add_header 'Access-Control-Allow-Origin' '*' always;
    }

    location / {
        root /var/www/html;
        index index.html;
        try_files $uri /index.html;
        add_header 'Access-Control-Allow-Origin' '*' always;
    }
}
```

---

## Запуск

> Для использования сервиса необходимы инфраструктурные сервисы (Redis, Rabbit, Postress) \
> Для их разворачивания воспользуйтесь репозиторием `lidar-back-infra` \
> <https://github.com/MindSetLib/lidar-back-infra>

1. Настройте `.env` (см. `env_example`).
2. Сборка фронтенда:

```bash
cd lidar_front
npm install
npm run build
cd ..
```

3. Добавьте файлы из архива weights.zip в  папку `lidar_detector/src/data`\
   В файле должны быть два файла:\
   \- voxelnext\_nuscenes\_kernel1.pth - веса модели детекции\
   \- cbgs\_voxel0075\_voxelnext.yaml - конфигурация модели\
   Путь к архиву: <https://disk.yandex.ru/d/_46DUs5XDbjGnw>
4. Запуск всех сервисов через Docker Compose:

```bash
docker-compose --build up -d
```

5. Откройте фронтенд, загрузите PCD-файл и следите за статусом обработки.

6. После завершения обработанный файл можно скачать через фронтенд или напрямую с `/files/`.