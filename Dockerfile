# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Conditionally copy the default database
ARG COPY_DB=false
RUN if [ "$COPY_DB" = "true" ]; then cp resources/template_database.db resources/database.db; fi

EXPOSE 5555

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5555", "--reload", "--ws", "websockets"]