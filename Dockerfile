FROM debian:buster-slim AS base

RUN apt-get update && \
        apt-get -y install --no-install-recommends \
        python3 python3-pip              \
        uwsgi uwsgi-plugin-python3    && \
        apt-get clean                 && \
        apt-get autoremove --yes      && \
        rm -rf /var/lib/apt/lists/*

RUN pip3 install docker

COPY static /logdok/static
COPY main.py /logdok/logdok.py
COPY logdok.ini /logdok/logdok.ini

VOLUME /logdok/static
VOLUME /var/run/docker.sock

EXPOSE 80

ENTRYPOINT ["uwsgi", "--ini", "/logdok/logdok.ini"]
