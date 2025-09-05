FROM postgres:15

RUN apt-get update && apt-get install -y cron

COPY backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh

RUN echo "*:*:*:migrator:sosiska" > /root/.pgpass && \
    chmod 600 /root/.pgpass

CMD ["/usr/local/bin/backup.sh"]