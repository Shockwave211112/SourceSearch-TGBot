# 🔍 SourceSearch Telegram Bot

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.26-blue.svg)](https://docs.aiogram.dev/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)

[Бот](https://t.me/SWPicFinderBot) для поиска первоисточников изображений (digital-арты). Отправьте картинку — получите ссылки на сайты, где она была опубликована.

## 📌 О проекте

Этот бот создан для дизайнеров, художников и администраторов каналов, которые хотят быстро находить авторов изображений и их источники. Он использует несколько поисковых систем, кэширует результаты и предоставляет удобный интерфейс для навигации.

### Основные возможности
*   **Поиск по изображению:** Отправьте фото, бот найдёт похожие или идентичные изображения в интернете.
*   **Мультипоиск:** Использует Danbooru IQDB и SauceNao для максимального покрытия.
*   **Умное кэширование:** Результаты сохраняются в БД, чтобы не повторять одинаковые запросы.
*   **Управление поиском:** Кнопки «Искать ещё», «Повторить последний поиск», «Искать везде заново».
*   **Лимиты:** Ограничение на количество API-запросов в день для одного пользователя.

## 🚀 Быстрый старт

### Предварительные требования
*   Python 3.11 или выше
*   Установленный Docker (опционально)
*   Токен Telegram бота (получить у [BotFather](https://t.me/BotFather))
*   API-ключи для SauceNao и Danbooru (см. раздел «Конфигурация»)

### Локальный запуск
1.  Клонируйте репозиторий:
    ```
    bash
    git clone https://github.com/Shockwave211112/SourceSearch-TGBot.git
    cd SourceSearch-TGBot
    ```

2.  Создайте и активируйте виртуальное окружение:
    ```
    python -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
    ```

3.  Установите зависимости:
    ```
    pip install -r requirements.txt
    ```

4.  Настройте переменные окружения:
    ```
    cp .env.example .env
    ```

5.  Примените миграции базы данных:
    ```
    alembic upgrade head
    ```

6.  Запустите бота:
    ```
    python main.py
    ```

### 🐳 Запуск с Docker
    docker compose up -d

## ⚙️ Конфигурация
| Переменная  | Описание | Где получить |
| ------------- | ------------- | ---------- |
| BOT_TOKEN  | Токен вашего Telegram бота  | [BotFather](https://t.me/BotFather) |
| SAUCENAO_API_KEY  | API-ключ для сервиса SauceNao  | [SauceNAO](https://saucenao.com/user.php) |
| DANBOORU_API_KEY | API-ключ для Danbooru | [Danbooru Wiki](https://danbooru.donmai.us/wiki_pages/api) |
| DANBOORU_LOGIN | Логин для доступа к Danbooru | [Danbooru Wiki](https://danbooru.donmai.us/wiki_pages/api) |
| USER_AGENT | 	Уникальный идентификатор вашего приложения (нужен для Danbooru поисковиков) | Придумайте сами (например, MySourceBot/1.0) |
| DANBOORU_DOMAIN | Домен Danbooru сайта (зеркала, тесты) | danbooru.donmai.us (по умолчанию) |
| USELESS_HOSTS | Список хостов, которые игнорируются в результатах | JSON-список, например ["twimg.com"] |
| DAILY_LIMIT | Лимит запросов на одного пользователя в день | Число, например 15 |
| OWNER_ID | Ваш Telegram ID (безлимит запросов) | Узнать у каких-либо ботов (к примеру, [userinfobot](https://t.me/userinfobot)) |

## 🛠️ Использовано
* Aiogram 3
* SQLAlchemy + Alembic 
* PicImageSearch
* Pillow
