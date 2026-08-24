# [file name]: docker/Dockerfile
# ============================================================
# VIREO DOCKER IMAGE
# ============================================================
# 
# Build:
#   docker build -t vireo:latest -f docker/Dockerfile .
#
# Run:
#   docker run -p 5000:5000 vireo:latest
#
# With Ollama (local):
#   docker run -p 5000:5000 -v ollama:/root/.ollama vireo:latest
#
# ============================================================

# ============================================================
# STAGE 1: BASE
# ============================================================

FROM python:3.11-slim AS base

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Встановлення робочої директорії
WORKDIR /app

# ============================================================
# STAGE 2: DEPENDENCIES
# ============================================================

FROM base AS dependencies

# Копіювання requirements
COPY requirements.txt .

# Встановлення Python залежностей
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# STAGE 3: APPLICATION
# ============================================================

FROM dependencies AS app

# Копіювання коду
COPY . .

# Створення необхідних папок
RUN mkdir -p models logs

# Відкриття порту
EXPOSE 5000

# ============================================================
# STAGE 4: PRODUCTION
# ============================================================

FROM app AS production

# Змінні середовища
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=api_server.py
ENV FLASK_ENV=production

# Запуск
CMD ["python", "api_server.py"]

# ============================================================
# STAGE 5: DEVELOPMENT
# ============================================================

FROM app AS development

ENV FLASK_ENV=development

# Встановлення додаткових інструментів для розробки
RUN pip install --no-cache-dir \
    black \
    mypy \
    pylint \
    pytest \
    pytest-cov

CMD ["python", "api_server.py"]

# ============================================================
# STAGE 6: WITH OLLAMA
# ============================================================

FROM app AS with-ollama

# Встановлення Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Завантаження моделі (опціонально, можна завантажити при першому запуску)
# RUN ollama pull qwen2.5-coder:latest

# Запуск Ollama та Vireo
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "api_server.py"]

# ============================================================
# STAGE 7: TEST
# ============================================================

FROM app AS test

# Запуск тестів
CMD ["pytest", "protocol/tests/", "-v", "--cov=."]

# ============================================================
# HEALTHCHECK
# ============================================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1