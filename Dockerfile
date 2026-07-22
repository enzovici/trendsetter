FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY config ./config
COPY alembic ./alembic
COPY alembic.ini ./

RUN pip install --no-cache-dir .

# Package is installed into site-packages; PROJECT_ROOT-relative config discovery
# would resolve into /usr/local/lib. Point at the copied config dir explicitly.
ENV CONFIG_DIR=/app/config

CMD ["uvicorn", "trendsetter.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
