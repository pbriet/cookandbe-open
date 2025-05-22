FROM public.ecr.aws/bitnami/postgresql:16

USER root

ENV LANG=fr_FR.UTF-8
RUN sed -i -e "s/# $LANG.*/$LANG UTF-8/" /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=$LANG

USER postgres

COPY 01-activate_pgsql_unaccent.sql /docker-entrypoint-initdb.d/
COPY 02-create-multiple-postgresql-db.sh /docker-entrypoint-initdb.d/
