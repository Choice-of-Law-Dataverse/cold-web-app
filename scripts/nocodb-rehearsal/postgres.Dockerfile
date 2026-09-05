ARG POSTGRES_VERSION=16
FROM postgres:${POSTGRES_VERSION}

RUN apt-get update \
    && apt-get install --yes --no-install-recommends "postgresql-${PG_MAJOR}-cron" \
    && rm -rf /var/lib/apt/lists/*
