FROM ubuntu:24.04

ENV TZ="Europe/Moscow"

WORKDIR /app

RUN apt update && apt upgrade -y && apt install -y --no-install-recommends \
    python3 \
    python3-venv

RUN python3 -m venv /venv

# To prevent the installation of dependencies after modifying project
# files, dependencies get installed before copying the project

COPY requirements.txt /app

RUN /venv/bin/pip install -r requirements.txt

# Now we can copy the project

COPY . /app

EXPOSE 9000

CMD ["/venv/bin/python", "main.py"]