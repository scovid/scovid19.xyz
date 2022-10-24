# syntax=docker/dockerfile:1.2

FROM python:3.10-slim-buster

LABEL Author="Daniel Stewart"
LABEL E-mail="danielandrewstewart@gmail.com"
LABEL version="0.0.1"

# Install deps
# Disable auto-cleanup after install:
RUN rm /etc/apt/apt.conf.d/docker-clean

# Install updates and cache across builds
ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,id=apt apt-get update && apt-get -y upgrade && apt-get install -y sudo cron sqlite3 curl vim

ENV PATH="/home/app/.local/bin:${PATH}"

# Add user, make sudo, do not require password
RUN useradd --create-home -G sudo app
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER app

# Configure sqlite
COPY --chown=app:app config/sqliterc /home/app/.sqliterc

RUN mkdir -p /home/app/scovid19
WORKDIR /home/app/scovid19

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install requirements
COPY --chown=app:app pyproject.toml ./
COPY --chown=app:app poetry.lock ./
RUN poetry install

# Get traceback for C crashes
ENV PYTHONFAULTHANDLER=1

COPY --chown=app:app . ./

EXPOSE 5000

# Blank entrypoint allows passing custom commands via `docker run`
ENTRYPOINT [ ]

CMD [ "/home/app/scovid19/entrypoint.sh" ]
