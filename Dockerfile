FROM python:3.8

LABEL Author="Daniel Stewart"
LABEL E-mail="danielandrewstewart@gmail.com"
LABEL version="0.0.1"

ENV FLASK_APP "src/app.py"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG True
ENV PATH="/home/code/.local/bin:${PATH}"

RUN useradd --create-home code
USER code

RUN mkdir -p /home/code/scovid19
WORKDIR /home/code/scovid19

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

EXPOSE 5000
CMD flask run --host=0.0.0.0
