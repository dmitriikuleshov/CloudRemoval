FROM pytorch/pytorch:2.5.0-cuda12.4-cudnn9-runtime

ENV TZ="Europe/Moscow"

ENV HF_HOME=/models

WORKDIR /app

RUN mkdir /models

# To prevent downloading dependencies again upon changing
# files, the dependencies file is copied separately
COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Now we can copy the remainder of the project
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]