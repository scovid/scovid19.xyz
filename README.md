# scovid19.xyz
The new and improved Scottish COVID-19 tracker.  

### Built with
- [flask](https://flask.palletsprojects.com/en/1.1.x/)
- [jinja](https://jinja.palletsprojects.com/en/2.11.x/)
- [Bulma](https://bulma.io/)
- [NHS OpenData API](https://www.opendata.nhs.scot/dataset)
- [Chart.js](https://www.chartjs.org/)
- [flatpickr](https://flatpickr.js.org/)
- [Plausible Analytics](https://plausible.io/)


## Running locally

Once done open http://127.0.0.1:5000 in your browser.  

#### With Docker
```bash
sudo apt install docker docker-compose
./control.sh --env dev --docker up

# Logs
docker logs --tail 200 -f scovid

docker exec -it scovid /bin/bash
tail -f src/app.log

# Tests
docker-compose build app
docker-compose run app pytest
# OR
docker exec -it scovid pytest
```

#### Without Docker
```bash
# Run (sets up virtualenv, installs dependencies and starts flask server)
./control.sh --env dev --flask up

# Logs
tail -f src/app.log

# Tests
pytest
```

## Deploy
#### With Docker
```bash
# Dependencies
sudo apt install docker docker-compose nginx certbot
sudo systemctl enable docker
sudo systemctl start docker

# run
./control.sh --env prod --docker up

# nginx
sudo cp nginx/scovid19.xyz /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/scovid19.xyz /etc/nginx/sites-enabled/
sudo service nginx restart

# Certbot
sudo certbot --nginx

# Update
git pull
./control.sh --docker deploy
```

#### Without Docker
```bash
# Dependencies
sudo apt install nginx certbot

# Create a virtualenv
python -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# systemd
sudo systemctl enable $(pwd)/system/systemd/scovid19.service
sudo systemctl start scovid19

# nginx
sudo cp system/nginx/scovid19.xyz /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/scovid19.xyz /etc/nginx/sites-enabled/
sudo service nginx restart

# Certbot
sudo certbot --nginx
```

### Notes
Open Data API reference:  
https://docs.ckan.org/en/latest/maintaining/datastore.html#api-reference
