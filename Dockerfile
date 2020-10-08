FROM python:3.8-slim-buster

LABEL Author="Daniel Stewart"
LABEL E-mail="danielandrewstewart@gmail.com"
LABEL version="0.0.1"

# Need to set this as an env var to use in the CMD below
ARG env='dev'
ENV ENV $env

ENV PATH="/home/code/.local/bin:${PATH}"

RUN useradd --create-home code
USER code

RUN mkdir -p /home/code/scovid19
WORKDIR /home/code/scovid19

COPY --chown=code:code requirements.txt ./
RUN pip install -r requirements.txt

COPY --chown=code:code . ./

EXPOSE 5000
CMD ./control.sh --env $ENV --flask up
