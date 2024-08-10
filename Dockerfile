# Указываем базовый образ с Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости
RUN pip install aiogram
RUN pip install saucenao-api
RUN pip install validators
RUN pip install environs
RUN pip install beautifulsoup4
RUN pip install Pillow
RUN pip install imagehash
RUN pip install cfscrape

# Копируем все файлы проекта в контейнер
COPY . .

# Указываем команду для запуска скрипта
CMD ["python", "main.py"]
