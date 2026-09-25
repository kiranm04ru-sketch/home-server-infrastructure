FROM postgres:16

ENV POSTGRES_USER=kmistry
ENV POSTGRES_PASSWORD=password123
ENV POSTGRES_DB=app_db

# Copy initialization script
COPY ./init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432
