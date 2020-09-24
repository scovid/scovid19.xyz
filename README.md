# scovid19.xyz
The new and improved Scottish COVID-19 tracker.  

### Built with
- [flask](https://flask.palletsprojects.com/en/1.1.x/)
- [jinja](https://jinja.palletsprojects.com/en/2.11.x/)
- [Bulma](https://bulma.io/)
- [NHS OpenData API](https://www.opendata.nhs.scot/dataset)
- [Chart.js](https://www.chartjs.org/)
- [flatpickr](https://flatpickr.js.org/)


## Running locally

#### With Docker/Podman
```bash
./control.sh --env dev --docker up

# Logs
sudo docker logs --tail 200 -f scovid-container

sudo docker exec -it scovid-container /bin/bash
tail -f src/app.log
```

#### Without Docker
```bash
# Create a virtualenv
python -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
./control.sh --env dev --flask up

# Logs
tail -f src/app.log
```

## Deploy
```bash
# Bootstrap
[[ -f /bootstrapped ]] || bash <(curl -s https://raw.githubusercontent.com/danstewart/server-bootstrap/master/bootstrap.sh)

# Create a virtualenv
python -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# selinux
cd system/selinux/
./install.sh scovid19.te

# systemd
sudo chcon -t bin_t /code/scovid19.xyz/system/systemd/scovid19.service
sudo systemctl enable /code/scovid19.xyz/system/systemd/scovid19.service
sudo service scovid19 start

# nginx
sudo cp system/nginx/scovid19.xyz /etc/nginx/sites-available/
sudo service nginx restart

# Start
sudo service start scovid19

# Certbot
sudo certbot --nginx
```

### Notes
Open Data API reference:  
https://docs.ckan.org/en/latest/maintaining/datastore.html#api-reference
