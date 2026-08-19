FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/
COPY static/ static/

ENV DB_PATH=/data/recomp.db
VOLUME ["/data"]
EXPOSE 8420

CMD ["python", "app.py"]
