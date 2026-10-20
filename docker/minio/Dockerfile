FROM golang:1.24 AS build
WORKDIR /source
RUN git init && git remote add origin https://github.com/minio/minio.git && git fetch --depth=1 origin 01ce918d8279a20e4706b96a64396146894adee4 && git checkout --detach FETCH_HEAD
RUN --mount=type=cache,target=/go/pkg/mod --mount=type=cache,target=/root/.cache/go-build CGO_ENABLED=0 go build -trimpath -o /minio .
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=build /minio /usr/local/bin/minio
EXPOSE 9000 9001
ENTRYPOINT ["minio"]
