FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY analysis analysis
COPY web web
ENV PORT=8000
CMD ["sh", "-c", "exec uvicorn web.demo:app --host 0.0.0.0 --port \"$PORT\""]
