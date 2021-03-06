FROM python:3.8.2-slim

COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

CMD ["python", "run.py"]
