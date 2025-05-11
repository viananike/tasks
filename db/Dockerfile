# Start from the official Postgres image
FROM postgres:13

# Copy the schema.sql file into the Postgres entrypoint directory
COPY ./init/schema.sql /docker-entrypoint-initdb.d/
