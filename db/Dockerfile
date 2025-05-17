# ./db/Dockerfile
FROM postgres:13

# Copy the schema.sql into the automatic init dir
COPY init/schema.sql /docker-entrypoint-initdb.d/
