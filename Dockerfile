# Используйте базовый образ Python
FROM python:3.9

# Копируем содержимое локальной папки wallet в контейнер
WORKDIR /app
COPY . /app

# Установка зависимостей из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install mysqlclient

RUN chmod +x main.py

EXPOSE 8000
