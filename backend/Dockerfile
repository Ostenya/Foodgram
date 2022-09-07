FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev build-essential gcc
RUN pip3 install -r /app/requirements.txt --no-cache-dir
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
CMD ["run"]