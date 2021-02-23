#!/usr/bin/env python3

import os, sys
import tweepy
import logging
from datetime import datetime
from scovid19.lib.Vaccine import Vaccine
from scovid19.lib.Infections import Infections

logging.basicConfig(
	filename=os.environ['PROJECT_ROOT'] + "/logs/bot.log",
	level=logging.INFO,
	format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
)

# Add your credentials here
twitter_keys = {
	"consumer_key": os.environ.get("SCOVID_TWITTER_API_KEY"),
	"consumer_secret": os.environ.get("SCOVID_TWITTER_API_SECRET"),
	"access_token_key": os.environ.get("SCOVID_TWITTER_ACCESS_TOKEN"),
	"access_token_secret": os.environ.get("SCOVID_TWITTER_ACCESS_SECRET"),
}

vaccine = Vaccine()
infections = Infections()

auth = tweepy.OAuthHandler(
	twitter_keys["consumer_key"], twitter_keys["consumer_secret"]
)
auth.set_access_token(
	twitter_keys["access_token_key"], twitter_keys["access_token_secret"]
)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

vaccine_data = vaccine.get_scraper_data()
infection_data = infections.summary()

daily_cases = f"{infection_data['cases']['today']:,.0f}"

date = datetime.today().strftime("%Y-%m-%d")

v = {
	"date": date,
	"dose1": f"{vaccine_data['dose1']:,.0f}",
	"dose2": f"{vaccine_data['dose2']:,.0f}",
	"daily_cases": daily_cases,
}
text = "Scotland vaccinations as of 08:30am on {date}: \n\n First Dose: {dose1} \n Second Dose: {dose2} \n\n {daily_cases} new infection cases confirmed \n\n For more stats visit www.scovid19.xyz"

if '--dry-run' in sys.argv:
	print(f"--dry-run passed, would be tweeeting the following message:\n{text.format(**v)}")
	sys.exit(0)

try:
	api.update_status(text.format(**v))
except tweepy.TweepError as e:
	logging.error("Error: " + e.response.text)
	sys.exit(1)
except tweepy.RateLimitError as e:
	logging.error("Error: " + e.response.text)
	sys.exit(1)
except:
	logging.error("Unknown Error.")
	sys.exit(1)
