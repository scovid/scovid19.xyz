# syntax=docker/dockerfile:1.2

FROM python:3.9-slim-buster

LABEL Author="Daniel Stewart"
LABEL E-mail="danielandrewstewart@gmail.com"
LABEL version="0.0.1"

# Install deps
# Disable auto-cleanup after install:
RUN rm /etc/apt/apt.conf.d/docker-clean

# Install updates and cache across builds
ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,id=apt apt-get update && apt-get -y upgrade && apt-get install -y sudo cron sqlite3 curl

ENV PATH="/home/code/.local/bin:${PATH}"

# Add user, make sudo, do not require password
RUN useradd --create-home -G sudo code
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER code

# Configure sqlite
RUN touch /home/code/.sqliterc
RUN echo ".headers on\n.mode columns" > /home/code/.sqliterc

RUN mkdir -p /home/code/scovid19
WORKDIR /home/code/scovid19

# Install python deps
COPY --chown=code:code requirements.txt ./
RUN pip install --upgrade pip
RUN --mount=type=cache,target=/home/app/.cache/pip,id=pip pip install -r requirements.txt

# Get traceback for C crashes
ENV PYTHONFAULTHANDLER=1

COPY --chown=code:code . ./

EXPOSE 5000

# Blank entrypoint allows passing custom commands via `docker run`
ENTRYPOINT [ ]

CMD [ "/home/code/scovid19/scovid19/entrypoint.sh" ]
