# Многостадийная сборка (первая стадия не нуждается в системных пакетах)
FROM python:3.11-slim as builder

WORKDIR /app

# Копируем только файл зависимостей
COPY requirements.txt .

# Устанавливаем Python-зависимости в пользовательскую директорию
RUN pip install --no-cache-dir --user -r requirements.txt

# Финальный образ
FROM python:3.11-slim

WORKDIR /app

# Копируем установленные пакеты из стадии builder
COPY --from=builder /root/.local /root/.local

# Копируем исходный код приложения
COPY . .

# Добавляем путь к пользовательским пакетам
ENV PATH=/root/.local/bin:$PATH

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]