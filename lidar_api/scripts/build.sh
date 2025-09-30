#!/bin/bash
set -e

# Чистим .env от хвостовых пробелов и Windows-CRLF
if [ -f .env ]; then
  echo ">>> Чистим .env..."
  sed -i 's/[[:space:]]*$//' .env     # убираем пробелы/табы в конце строк
  sed -i 's/\r$//' .env               # убираем CR (если файл в Windows-формате)
else
  echo ">>> Файл .env не найден!"
  exit 1
fi

# Загружаем переменные окружения
set -a
source .env
set +a

echo ">>> Собираем образ $IMAGE_NAME..."
docker build \
  --build-arg GITLAB_USER=${GITLAB_USER} \
  --build-arg GITLAB_TOKEN=${GITLAB_TOKEN} \
  --build-arg IS_DEV=${IS_DEV} \
  -t $IMAGE_NAME .
