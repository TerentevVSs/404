FROM almalinux:8.6

RUN dnf update -y && dnf install wget yum-utils make gcc openssl-devel bzip2-devel libffi-devel zlib-devel -y
RUN wget https://www.python.org/ftp/python/3.10.2/Python-3.10.2.tgz && tar xzf Python-3.10.2.tgz
WORKDIR /Python-3.10.2
RUN ./configure --with-system-ffi --with-computed-gotos --enable-loadable-sqlite-extensions && make && make altinstall

WORKDIR /app
ADD ./requirements.txt /
RUN python3.10 -m pip install -r /requirements.txt --no-cache-dir

ADD ./backend.service /etc/systemd/system/

RUN set -ex \
    && systemctl enable backend.service


ARG POSTGRES_HOST
ARG POSTGRES_PORT
ARG POSTGRES_DB
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD

ARG DEBUG

ARG PROJECT_NAME
ARG PROJECT_DESCRIPTION
ARG SERVER_NAME
ARG VERSION
ARG PRETRAINED_MODEL_CACHE_DIR
ARG APP_PORT

EXPOSE ${APP_PORT}

ADD . /app
RUN /bin/sh /app/create_env.sh > /etc/sysconfig/backend