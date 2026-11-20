FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Core is stdlib-only; no network needed at build or run (air-gap safe).
ENV KAVACH_HOST=0.0.0.0 \
    KAVACH_PORT=8765 \
    PYTHONUNBUFFERED=1

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8765/health').getcode()==200 else 1)"

CMD ["python", "-m", "kavach.console.server"]
