# Utils ML lib

Библиотека содержит часто используемые скрипты для проекта `pr_innosety_ocr` - Сервис распознования документов

## Содержание

1. [Версионность](#версионность)
2. [Deploy](#deploy)
3. [Установка](#установка)
4. [Полезная документация](#полезная-документация)

## Версионность

Для управления версионностью (Gitlab не позволяет опубликовать пакет с одной и той же версией) необходимо указать версию пакета в двух местах:

1. `pyproject.toml` - тут можно обновить версию через командую строку используя следующую команду:

например, если необходимо обновить `patch`. Дополнительно можно почитать про версионирование [тут](https://python-poetry.org/docs/cli/#version)

```bash
poetry version patch
```

2. `setup.py` - тут в поле `version` так же указываем версию (ту же, что и в `pyproject.toml`)

## Deploy

После того как код был запушен в `main` ветку, необходимо выпустить `release`:

```
Переходим в Gitlab project -> Deployments -> Releases -> New release
```

Далее необходимо указать `Tag name` и `Release title`:

```
В нем указываем версию которую прописали на предыдущем шаге в файле `setup.py`, жмем создать новый тег из ветки `main`
```

Готово! Ждем когда пакет сбилдится и опубликуется

## Установка

После сборки и публикации можно будет устанавливать ваш пакет как обычно:

```bash
poetry source add ocr-configurations "https://gitlab.innoseti.ru/api/v4/projects/1003/packages/pypi/simple"
poetry add --source ocr-configurations ocr-configurations
```

Если пакет находится в приватном репозитории, необходимо так же настроить аутентификацию (для GitLab Package Registry рекомендую использовать [Personal Access Token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)):

```bash
poetry config http-basic.ocr-configurations <token-name> <secret-token>
```

Установка:

```bash
poetry install
```

## Полезная документация

* Официальная документация [Poetry](https://python-poetry.org/docs/)
* Статья на Хабре: [Poetry: from zero to hero](https://habr.com/ru/articles/740376/)