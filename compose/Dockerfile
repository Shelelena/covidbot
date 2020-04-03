FROM python:3.8-slim

COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r ./compose/requirements.txt

CMD ["python", "run.py"]
