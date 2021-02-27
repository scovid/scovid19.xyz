## Set up

Create a `.env` file in the root of the project with the following items
```
# Config
PROJECT_ROOT=''

# Twitter credentials
SCOVID_TWITTER_API_KEY=''
SCOVID_TWITTER_API_SECRET=''
SCOVID_TWITTER_ACCESS_TOKEN=''
SCOVID_TWITTER_ACCESS_SECRET=''
```

## Running
```
cd $SCOVID_PROJECT_ROOT && python3 -m scovid19.scripts.tweet [--dry-run]
```
