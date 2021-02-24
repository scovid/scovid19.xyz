FROM python:3.8-slim-buster

LABEL Author="Daniel Stewart"
LABEL E-mail="danielandrewstewart@gmail.com"
LABEL version="0.0.1"

# Install deps
RUN apt-get update -y && apt-get install -y sudo cron

# Need to set this as an env var to use in the CMD below
ARG env='dev'
ENV ENV $env

ENV PATH="/home/code/.local/bin:${PATH}"

# Add user, make sudo, do not require password
RUN useradd --create-home -G sudo code
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER code

RUN mkdir -p /home/code/scovid19
WORKDIR /home/code/scovid19

COPY --chown=code:code requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY --chown=code:code . ./

# Don't need a .env in the container
# env is set by docker-compose
RUN if [ -f .env ]; then rm .env; fi

EXPOSE 5000
ENTRYPOINT [ "/home/code/scovid19/scovid19/entrypoint.sh" ]
