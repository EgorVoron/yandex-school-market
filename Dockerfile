FROM python:3

WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["waitress-serve", "--port=80", "wsgi:app"]