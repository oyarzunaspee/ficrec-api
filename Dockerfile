FROM python:3.13.1

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]