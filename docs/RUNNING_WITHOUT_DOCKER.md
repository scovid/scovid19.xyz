# Running locally without docker

### Clone
```bash
git clone git@github.com:scovid/scovid19.xyz.git
cd scovid19.xyz
```

### Install pyenv and python 3.10.0
```bash
curl https://pyenv.run | bash
exec $SHELL
pyenv install 3.10.0
pyenv local 3.10.0
```

### Install poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -

# It is recommended to store your virtualenv within the project - but this is optional
poetry config virtualenvs.in-project true

# Point poetry to your pyenv install of python 3.10
poetry env add $HOME/.pyenv/shims/python3.10

# Install dependencies
poetry install
```

### Download data and run
```bash
poetry run tools/update_db.py

# Set environment
export FLASK_APP=app
export FLASK_ENV=dev
export SCOVID_ENV=dev
export DATABASE=./data/scovid19.db
export SCOVID_PROJECT_ROOT=$(pwd)

# Run
poetry run flask run --port 1234
```


### Running tests
```bash
poetry run pytest
poetry run bandit .
```
