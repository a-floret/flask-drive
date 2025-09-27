FROM python:3.12-slim
WORKDIR /app
COPY flaskr .
RUN pip install flask psycopg2-binary python-dotenv password-validator
CMD ["python","drive.py"]
