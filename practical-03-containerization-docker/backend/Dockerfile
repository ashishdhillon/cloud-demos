FROM python:3.12-slim

# Create unprivileged application user
RUN groupadd -g 10001 cloudapp && \
    useradd -u 10001 -g cloudapp -m -s /bin/bash cloudapp

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY cgroup_engine.py app.py .

RUN chown -R cloudapp:cloudapp /app /tmp

USER 10001

EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/healthz')"

CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "1", "--threads", "8", "app:app"]
