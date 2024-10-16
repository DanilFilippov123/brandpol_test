FROM python:3.12-bookworm
LABEL authors="danil"

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["gunicorn", "-b 0.0.0.0:8000", "brandpol_test.wsgi:application"]