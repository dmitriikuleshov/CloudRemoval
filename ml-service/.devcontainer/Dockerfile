FROM pytorch/pytorch:2.5.0-cuda12.4-cudnn9-runtime

ENV TZ="Europe/Moscow"

WORKDIR /app

RUN apt update && apt upgrade -y

RUN apt install -y --no-install-recommends python3 python3-venv

RUN python3 -m venv /venv

# To prevent downloading dependencies again upon changing
# files, the dependencies file is copied separately
COPY ../requirements.txt .

RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Now we can copy the remainder of the project
COPY . /app

EXPOSE 8000

CMD ["/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]