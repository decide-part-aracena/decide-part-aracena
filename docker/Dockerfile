from python:3.8-buster

RUN apt-get update
RUN apt-get -y install git postgresql gcc libc-dev
RUN apt-get -y install gcc g++ make libffi-dev python3-dev build-essential

RUN pip install gunicorn
RUN pip install psycopg2
RUN pip install ipdb
RUN pip install ipython

WORKDIR /app

RUN git clone https://github.com/decide-part-aracena/decide-part-aracena.git .
RUN pip install -r requirements.txt

WORKDIR /app/decide

# local settings.py
ADD docker-settings.py /app/decide/local_settings.py

RUN ./manage.py collectstatic

#CMD ["gunicorn", "-w 5", "decide.wsgi", "--timeout=500", "-b 0.0.0.0:5000"]
