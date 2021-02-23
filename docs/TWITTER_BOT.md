## Set up

Create a `secrets.bash` file in the root of the project with the following items
```
# Config
export PROJECT_ROOT=''

# Twitter credentials
export SCOVID_TWITTER_API_KEY=''
export SCOVID_TWITTER_API_SECRET=''
export SCOVID_TWITTER_ACCESS_TOKEN=''
export SCOVID_TWITTER_ACCESS_SECRET=''
```

## Running
```
cd $PROJECT_ROOT && python3 -m scovid19.scripts.tweet [--dry-run]
```
