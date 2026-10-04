FROM postgres:16

# Credentials and database name are injected at runtime by docker-compose.yml
# from the git-ignored .env file — nothing sensitive is baked into the image.
# init.sql runs only on first initialization of the postgres_data volume.

# Copy initialization script
COPY ./init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432
