FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run migrations, create initial data, then start the server
# We use ${PORT:-8000} to let Render set the port dynamically
CMD sh -c "alembic upgrade head && python -m app.initial_data && python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"