FROM --platform=linux/amd64 python:3.9.6-slim
WORKDIR /app
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN pip install python-multipart

COPY . /app

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]
