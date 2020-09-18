# scovid19.xyz
The new and improved Scottish COVID-19 tracker.  

### Built with
- [flask](https://flask.palletsprojects.com/en/1.1.x/)
- [jinja](https://jinja.palletsprojects.com/en/2.11.x/)
- [Bulma](https://bulma.io/)
- [NHS OpenData API](https://www.opendata.nhs.scot/dataset)
- [Chart.js](https://www.chartjs.org/)
- [flatpickr](https://flatpickr.js.org/)


### Install
```
# Bootstrap
[[ -f /bootstrapped ]] || bash <(curl -s https://raw.githubusercontent.com/danstewart/server-bootstrap/master/bootstrap.sh)

# Create a virtualenv
python -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# nginx
sudo cp nginx/scovid19.xyz /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/scovid19.xyz /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Certbot
sudo certbot --nginx
```

### Starting
Start dev server:
```
source venv/bin/activate
python src/app.pl
```

Start prod server:
```
# TODO
```

### Notes
Open Data API reference:  
https://docs.ckan.org/en/latest/maintaining/datastore.html#api-reference
