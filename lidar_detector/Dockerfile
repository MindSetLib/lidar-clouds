FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04

# Каталоги
ENV HOME=/home/app
ENV APP_HOME=/home/app/src
ENV PYTHONPATH=${HOME}
# Добавление пути до poetry
ENV PATH="${HOME}/.local/bin:$PATH"
# Путь до python 3.9
ENV PYTHONPATH="${HOME}:/usr/lib/python3.9/site-packages:/usr/local/lib/python3.9/dist-packages:$PATH"

# Системное время
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Для установки без вопрсов пользователю, неинтерактивный режим
ENV DEBIAN_FRONTEND=noninteractive
# Видимость видеокарт
ENV NVIDIA_VISIBLE_DEVICES=all

# Переменные pip и poetry
ENV POETRY_VERSION=2.1.3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Устанавливаем переменную от какого пользователя будет работать сервис
ENV RUNASUSER=1234
ENV USERNAME=app

# переключатель: устанавливать dev-зависимости poetry или нет
ARG IS_DEV


# Добавление репозитория
RUN apt update && apt install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa


# Установка Python и других пакетов
RUN apt update && apt install -y --no-install-recommends \
    g++ \
    python3.9 \
    python3.9-distutils \
    python3.9-dev \
    git \
    wget \
    curl \
    libgl1 \
    poppler-utils \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt clean -y && apt autoclean -y && rm -rf /var/lib/apt/lists/*


# Установка pip и необходимых инструментов для Python 3.9
RUN wget https://bootstrap.pypa.io/get-pip.py \
    && python3.9 get-pip.py \
    && rm get-pip.py \
    && pip3.9 install -U pip setuptools \
    && ln -s /usr/bin/python3.9 /usr/bin/python \
    && ln -s /usr/bin/pip3.9 /usr/bin/pip \
    && rm -rf /var/lib/apt/lists/*

# Установка poetry
RUN apt update && apt install -y \
    python3-dev \
    build-essential && \
    curl -sSL https://install.python-poetry.org | python3.9 - && \
    apt clean -y && apt autoclean -y && rm -rf /var/lib/apt/lists/*


WORKDIR $APP_HOME


# Установка специфичных и тяжелых зависимостей
RUN --mount=type=cache,target=/root/.cache \
    pip install \
        --find-links https://download.pytorch.org/whl/torch_stable.html \
        torch==1.10.0+cu111 \
        torchvision==0.11.0+cu111 \
        torchaudio==0.10.0


RUN --mount=type=cache,target=/root/.cache \
    pip install  \
        timm==0.9.2 \
        ultralytics==8.3.103

RUN --mount=type=cache,target=/root/.cache \
    pip install \
    --find-links https://dl.fbaipublicfiles.com/detectron2/wheels/cu111/torch1.10/index.html \
    detectron2

COPY pyproject.toml poetry.lock ./
# Установка Python-зависимостей через Poetry
# любое значение кроме "true" считается прод-сборкой
# docker build --build-arg IS_DEV=true -t myapp:dev .
RUN $(test "$IS_DEV" != "true" && echo "--only=main") \
      --no-interaction --no-ansi \
      --no-root && \
    rm -f $HOME/.config/pypoetry/auth.toml

# Создаем пользователя и директории
RUN groupadd -g ${RUNASUSER} -r ${USERNAME} && \
    useradd -u ${RUNASUSER} -r -g ${USERNAME} -d ${HOME} -s /sbin/nologin -c "Docker image user" ${USERNAME} && \
    chown -R ${USERNAME}:${USERNAME} ${APP_HOME}
