FROM python:3.12.3-slim

# Каталоги
ENV HOME=/home/app
ENV APP_HOME=/home/app/src
ENV PYTHONPATH=${HOME}
# Добавление пути до poetry
ENV PATH="${HOME}/.local/bin:$PATH"

# Системное время
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Для установки без вопрсов пользователю, неинтерактивный режим
ENV DEBIAN_FRONTEND=noninteractive

# Переменные pip и poetry
ENV POETRY_VERSION=2.1.3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# устанавливаем переменную от какого пользователя будет работать сервис
ENV RUNASUSER=1234
ENV USERNAME=app

# переключатель: устанавливать dev-зависимости poetry или нет
ARG IS_DEV


# Добавление репозиториев
RUN apt update && apt install -y \
    software-properties-common \
    python3-launchpadlib && \
    add-apt-repository ppa:libreoffice/ppa

# Установка пакетов
RUN apt update && apt install -y \
    netcat-traditional \
    poppler-utils && \
    apt clean -y && apt autoclean -y && rm -rf /var/lib/apt/lists/*

# Установка poetry
RUN apt update && apt install -y \
    curl \
    python3-dev \
    g++ \
    cython3 \
    build-essential && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt clean -y && apt autoclean -y && rm -rf /var/lib/apt/lists/*

WORKDIR $APP_HOME

COPY pyproject.toml poetry.lock ./
# Установка Python-зависимостей через Poetry
# любое значение кроме "true" считается прод-сборкой
# docker build --build-arg IS_DEV=true -t myapp:dev .
RUN poetry install \
      $(test "$IS_DEV" != "true" && echo "--only=main") \
      --no-interaction --no-ansi \
      --no-root && \
    rm -f $HOME/.config/pypoetry/auth.toml

# Создаем пользователя и директории
RUN groupadd -g ${RUNASUSER} -r ${USERNAME} && \
    useradd -u ${RUNASUSER} -r -g ${USERNAME} -d ${HOME} -s /sbin/nologin -c "Docker image user" ${USERNAME} && \
    chown -R ${USERNAME}:${USERNAME} ${APP_HOME}

USER ${USERNAME}
