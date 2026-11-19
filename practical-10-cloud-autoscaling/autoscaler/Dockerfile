FROM python:3.12-slim

WORKDIR /autoscaler

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docker_manager.py autoscaler.py .

ENV PYTHONUNBUFFERED=1

EXPOSE 9000

CMD ["python", "autoscaler.py"]