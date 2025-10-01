FROM nvidia/cuda:11.7.1-devel-ubuntu22.04

# -----------------------------
# Настройки окружения
# -----------------------------
ENV HOME=/home/app
ENV APP_HOME=/home/app/src
ENV PYTHONPATH=${HOME}
ENV PATH="${HOME}/.local/bin:$PATH"
ENV TZ=Europe/Moscow
ENV DEBIAN_FRONTEND=noninteractive
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

ENV RUNASUSER=1234
ENV USERNAME=app

ARG IS_DEV

# -----------------------------
# Системное время
# -----------------------------
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# -----------------------------
# Добавление репозитория и установка Python 3.9
# -----------------------------
RUN apt update && apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && apt install -y --no-install-recommends \
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
        ca-certificates \
    && apt clean -y && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Настройка pip и Python 3.9
# -----------------------------
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.9 get-pip.py && \
    rm get-pip.py && \
    pip3.9 install --upgrade pip setuptools wheel && \
    ln -sf /usr/bin/python3.9 /usr/bin/python && \
    ln -sf /usr/bin/pip3.9 /usr/bin/pip

# -----------------------------
# Установка Poetry
# -----------------------------
RUN curl -sSL https://install.python-poetry.org | python3.9 - && \
    rm -rf /var/lib/apt/lists/*

WORKDIR $APP_HOME

# -----------------------------
# Heavy-binary зависимости через pip
# -----------------------------
RUN pip install --upgrade \
        torch==2.0.1+cu117 \
        torchvision==0.15.2+cu117 \
        torchaudio==2.0.2+cu117 \
        --index-url https://download.pytorch.org/whl/cu117 \
        --find-links https://download.pytorch.org/whl/cu117/torch_stable.html

RUN pip install spconv-cu117==2.3.6

RUN pip install 'git+https://github.com/facebookresearch/detectron2.git'

# -----------------------------
# OpenPCDet
# -----------------------------
RUN git clone https://github.com/open-mmlab/OpenPCDet.git /workspace/OpenPCDet
WORKDIR /workspace/OpenPCDet
RUN pip install --upgrade "setuptools<65" wheel
ENV TORCH_CUDA_ARCH_LIST="7.0+PTX;8.6+PTX"
RUN pip install -e . --no-deps --no-build-isolation

# -----------------------------
# Дополнительные пакеты
# -----------------------------
RUN pip install timm==0.9.2 ultralytics==8.3.103

# -----------------------------
# Poetry зависимости (pure-Python)
# -----------------------------
WORKDIR $APP_HOME
COPY pyproject.toml poetry.lock ./

# Удаляем конфликтные системные пакеты, чтобы Poetry смог обновить
RUN apt remove -y python3-blinker || true

# Здесь Poetry ставит только чистые Python зависимости
RUN poetry install \
      $(test "$IS_DEV" != "true" && echo "--only=main") \
      --no-interaction --no-ansi --no-root && \
    rm -f $HOME/.config/pypoetry/auth.toml
# -----------------------------
# Утилиты
# -----------------------------
RUN apt update && apt install -y iputils-ping dnsutils netcat && apt clean -y

# -----------------------------
# Создание пользователя
# -----------------------------
RUN groupadd -g ${RUNASUSER} -r ${USERNAME} && \
    useradd -u ${RUNASUSER} -r -g ${USERNAME} -d ${HOME} -s /sbin/nologin -c "Docker image user" ${USERNAME} && \
    chown -R ${USERNAME}:${USERNAME} $APP_HOME /workspace/OpenPCDet

WORKDIR $APP_HOME
