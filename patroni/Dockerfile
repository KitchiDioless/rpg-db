FROM postgres:15-alpine

RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    python3-dev \
    postgresql-dev \
    linux-headers \
    gettext \
    su-exec \
    bash \
    postgresql-contrib \
    wget

ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

RUN wget https://github.com/prometheus-community/postgres_exporter/releases/download/v0.15.0/postgres_exporter-0.15.0.linux-amd64.tar.gz && \
    tar xvf postgres_exporter-0.15.0.linux-amd64.tar.gz && \
    mv postgres_exporter-0.15.0.linux-amd64/postgres_exporter /usr/local/bin/ && \
    rm -rf postgres_exporter-0.15.0.linux-amd64*

RUN mkdir -p /usr/lib/postgresql/15/bin && \
    for cmd in initdb pg_ctl postgres pg_controldata pg_isready pg_basebackup psql; do \
        ln -s /usr/local/bin/$cmd /usr/lib/postgresql/15/bin/$cmd; \
    done

RUN pip3 install --break-system-packages \
    patroni[etcd3]==3.2.2 \
    psycopg2-binary==2.9.9 \
    python-etcd==0.4.5 \
    urllib3

RUN mkdir -p /etc/patroni /var/log/patroni /home/postgres /tmp/archive && \
    chmod 777 /tmp/archive

COPY patroni.yml /etc/patroni/patroni.yml
COPY entrypoint.sh /entrypoint.sh
COPY init.sql /init.sql
RUN chmod +x /entrypoint.sh

EXPOSE 5432 8008 9187

ENTRYPOINT ["/entrypoint.sh"]