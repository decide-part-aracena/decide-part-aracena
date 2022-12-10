FROM python:3.8-buster

RUN apt-get update
RUN apt-get -y install git postgresql gcc libc-dev
RUN apt-get -y install gcc g++ make libffi-dev python3-dev build-essential

RUN pip install gunicorn
RUN pip install psycopg2
RUN pip install ipdb
RUN pip install ipython

WORKDIR /app
COPY decide ./decide
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt


WORKDIR /app/decide
# local settings.py
COPY docker/web/docker_settings.py ./local_settings.py
# copy secrets settings only if exist
COPY docker/dummy decide/secrets_settings.py* ./
RUN ./manage.py collectstatic

#CMD ["gunicorn", "-w 5", "decide.wsgi", "--timeout=500", "-b 0.0.0.0:5000"]
