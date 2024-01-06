FROM debian:latest

LABEL org.opencontainers.image.title bebop
LABEL org.opencontainers.image.authors @joshhighet
LABEL org.opencontainers.image.base.name ghcr.io/joshhighet/bebop:latest
LABEL org.opencontainers.image.description scanner
LABEL org.opencontainers.image.documentation https://github.com/joshhighet/bebop#readme
LABEL org.opencontainers.image.url https://github.com/joshhighet/bebop/pkgs/container/bebop
LABEL org.opencontainers.image.source https://github.com/joshhighet/bebop/blob/main/bebop/dockerfile

RUN apt update --yes
RUN apt install --yes proxychains-ng nmap python3-pip jq

ARG SOCKS_PORT=9050
ARG SOCKS_HOST=127.0.0.1
ENV SOCKS_PORT=$SOCKS_PORT
ENV SOCKS_HOST=$SOCKS_HOST
ENV PYTHONUNBUFFERED True
COPY . ./
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "-m", "app"]