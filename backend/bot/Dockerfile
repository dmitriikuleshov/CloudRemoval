FROM python:3.12-alpine

ENV TZ="Europe/Moscow"

WORKDIR /app

# To prevent the installation of dependencies after modifying project
# files, dependencies get installed before copying the project

COPY ./bot/requirements.txt /app

RUN pip install -r /app/requirements.txt

# Now we can copy the project
COPY ./bot /app/
COPY ./common /app/common

EXPOSE 9000

CMD ["python", "main.py"]
