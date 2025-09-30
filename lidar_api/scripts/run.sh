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

# Проверка обязательных переменных
for var in IMAGE_NAME CONTAINER_NAME NETWORK_NAME HOST_NAME; do
  if [ -z "${!var}" ]; then
    echo ">>> Ошибка: переменная $var не определена в .env"
    exit 1
  fi
done

# Запускаем контейнер
echo ">>> Запускаем контейнер $CONTAINER_NAME..."
docker run -d \
  --name $CONTAINER_NAME \
  --hostname $HOST_NAME \
  --network $NETWORK_NAME \
  --restart unless-stopped \
  --env-file .env \
  -p ${APP_PORT}:8000 \
  -v $(pwd)/src:/home/app/src \
  -v ${DATA_PATH}/file_storage:/home/app/src/file_storage \
  -v /home/mindset_dev/dev/lidar-clouds/ocr_configurations/ocr_configurations:/home/app/src/ocr_configurations \
  $IMAGE_NAME \
  python3 main.py

echo ">>> Контейнеры:"
docker ps --filter "name=$CONTAINER_NAME"
