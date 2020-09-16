# scovid19.xyz
The new and improved Scottish COVID-19 tracker.  

### Built with
- [mojolicious](https://mojolicious.org/)
- [Bulma](https://bulma.io/)
- [NHS OpenData API](https://www.opendata.nhs.scot/dataset)
- [Chart.js](https://www.chartjs.org/)
- [flatpickr](https://flatpickr.js.org/)


### Install
```
# Bootstrap
[[ -f /bootstrapped ]] || bash <(curl -s https://raw.githubusercontent.com/danstewart/server-bootstrap/master/bootstrap.sh)

dnf install openssl-devel zlib-devel

# Install plenv
git clone https://github.com/tokuhirom/plenv.git ~/.plenv
echo 'export PATH="$HOME/.plenv/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(plenv init -)"' >> ~/.bash_profile
git clone https://github.com/tokuhirom/Perl-Build.git ~/.plenv/plugins/perl-build/

# Install perl
plenv install 5.32.0
plenv rehash
plenv global 5.32.0
plenv install-cpanm

# Install carton
cpanm Carton

# Install dependencies
carton install

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
carton exec morbo src/app.pl -w ./src
```

Start prod server:
```
carton exec hypnotoad src/app.pl

# and stop with
carton exec hypnotoad src/app.pl --stop
```

### Notes
Open Data API reference:  
https://docs.ckan.org/en/latest/maintaining/datastore.html#api-reference
