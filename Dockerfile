FROM python:3.9
ENV PYTHONUNBUFFERED 1
ENV HTTP_PROXY =https://10.102.162.14:3128

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
COPY . /app

CMD python manage.py wait_for_db && python manage.py runserver 0.0.0.0:8000
