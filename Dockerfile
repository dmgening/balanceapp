 FROM python:3.5
 ENV PYTHONUNBUFFERED 1
 ENV DJANGO_SETTINGS_MODULE balanceapp.settings

 RUN mkdir /app
 WORKDIR /app
 ADD . /app

 RUN pip install -r requirements.txt && \
     pip install -e .
