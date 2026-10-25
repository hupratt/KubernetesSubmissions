
FROM python:3.13-slim

# tells Python not to buffer stdout and stderr, so anything you print() is written out immediately
ENV PYTHONUNBUFFERED=1
 
WORKDIR /app
COPY main.py .
 
RUN useradd --no-create-home --shell /usr/sbin/nologin appuser
USER appuser
EXPOSE 8000

CMD ["python", "main.py"]
 
