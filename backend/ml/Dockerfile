FROM pytorch/pytorch:2.5.0-cuda12.4-cudnn9-runtime

ENV TZ="Europe/Moscow"

ENV HF_HOME=/models

WORKDIR /app

RUN mkdir /models

# To prevent downloading dependencies again upon changing
# files, the dependencies file is copied separately
COPY ml/requirements.txt /app

RUN pip install -r /app/requirements.txt

# Now we can copy the remainder of the project
COPY ./ml /app
COPY ./common /app/common

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
