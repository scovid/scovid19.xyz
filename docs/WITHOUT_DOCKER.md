### Running locally
```bash
# Run (sets up virtualenv, installs dependencies and starts flask server)
SCOVID_PROJECT_ROOT=$(pwd) ./control.sh --env dev --flask up

# Logs
tail -f logs/app.log

# Tests
pytest

# Formatting
python -m tan --use-tabs scovid19/
```

### Deploy
```bash
# Dependencies
sudo apt install nginx certbot

# Create a virtualenv
python -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# nginx
sudo cp config/nginx/scovid19.xyz /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/scovid19.xyz /etc/nginx/sites-enabled/
sudo service nginx restart

# Certbot
sudo certbot --nginx
```
