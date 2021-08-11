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


## How to

The following instructions use docker, if you'd rather not use docker then see `docs/WITHOUT_DOCKER.md`.  

### Run locally
```bash
# Dependencies
sudo apt install docker docker-compose

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export BUILDKIT_PROGRESS=plain

# Start the container in dev mode
docker-compose up -d --build scovid

# Logs
docker logs --tail 200 -f scovid

# Tests
docker exec -it scovid pytest
```

### Deploy
```bash
# Dependencies
sudo apt install docker docker-compose nginx certbot
sudo systemctl enable docker
sudo systemctl start docker

# run
docker-compose -f docker-compose.yml up -d --build scovid

# nginx
sudo cp nginx/scovid19.xyz /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/scovid19.xyz /etc/nginx/sites-enabled/
sudo service nginx restart

# Certbot
sudo certbot --nginx

# Update
# Uses docker-compose scaling to deploy without downtime
git pull
./tools/deploy.sh
```


## Notes
Open Data API reference:  
https://docs.ckan.org/en/latest/maintaining/datastore.html#api-reference
