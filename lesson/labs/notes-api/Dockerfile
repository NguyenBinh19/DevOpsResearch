FROM python:3.13-slim
WORKDIR /app
COPY app.py /app/app.py
RUN mkdir /data && chown 10001:10001 /data
USER 10001:10001
ENV NOTES_HOST=0.0.0.0 NOTES_PORT=8000 NOTES_DB=/data/notes.db
EXPOSE 8000
CMD ["python", "/app/app.py"]
