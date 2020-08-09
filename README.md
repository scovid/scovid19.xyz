# scovid19.xyz
The new and improved Scottish COVID-19 tracker.  


### Get started

Setup:
```
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
```

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


#### Notes

Open Data API reference:  
https://docs.ckan.org/en/latest/maintaining/datastore.html#api-reference
