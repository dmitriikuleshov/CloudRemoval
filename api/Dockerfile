FROM python:3.12-alpine


ENV TZ="Europe/Moscow"

WORKDIR /app

# To prevent the installation of dependencies after modifying project
# files, dependencies get installed before copying the project

COPY requirements.txt /app

RUN pip install -r requirements.txt

# Now we can copy the project

COPY . /app

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]