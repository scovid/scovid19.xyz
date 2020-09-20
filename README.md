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

# selinux
cd selinux/
./install.sh scovid19.te

# systemd
sudo chcon -t bin_t /code/scovid19.xyz/system/systemd/scovid19.service
sudo systemctl enable /code/scovid19.xyz/system/systemd/scovid19.service
sudo systemctl start nginx

# nginx
sudo cp system/nginx/scovid19.xyz /etc/nginx/sites-available/

# Certbot
sudo certbot --nginx
```

### Starting
Start dev server:
```
source venv/bin/activate
cd src/
FLASK_APP=app.py FLASK_ENV=development flask run
```

Start prod server:
```
# TODO
```

### Notes
Open Data API reference:  
https://docs.ckan.org/en/latest/maintaining/datastore.html#api-reference
