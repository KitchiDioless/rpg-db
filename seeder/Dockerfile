FROM python:3.11-slim
WORKDIR /app
COPY seed.py wait-for-it.sh create_analitycs.py ./
RUN pip install --no-cache-dir psycopg2-binary faker packaging prometheus_client
RUN chmod +x wait-for-it.sh
ENTRYPOINT ["sh", "-c", "./wait-for-it.sh db:5432 -- && python create_analitycs.py && python seed.py"]
