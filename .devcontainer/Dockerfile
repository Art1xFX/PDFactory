# Note: You can use any Debian/Ubuntu based image you want.
FROM mcr.microsoft.com/devcontainers/base:trixie@sha256:30b0a0c004ca94d36c323ee993361a7e0ae25ea255ea125201e8a9587501c324

RUN apt-get update && \
    apt-get install -y --no-install-recommends --no-install-suggests \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        fontconfig \
        fonts-dejavu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
