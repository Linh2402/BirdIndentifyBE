FROM python:3.9

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5005

EXPOSE 5005

CMD ["flask", "run"]