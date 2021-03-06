#!/usr/bin/env python3

import os, sys
import tweepy
from datetime import datetime
from scovid19.lib.data.Vaccines import Vaccines
from scovid19.lib.data.Infections import Infections
from scovid19.lib.Util import get_logger, project_root


def main(dry_run=False):
	# Disable caching to always pull latest stats
	os.environ['SCOVID_NO_CACHE'] = '1'

	tweet_logger = get_logger("tweet_bot")

	# Add your credentials here
	twitter_keys = {
		"consumer_key": os.environ.get("SCOVID_TWITTER_API_KEY"),
		"consumer_secret": os.environ.get("SCOVID_TWITTER_API_SECRET"),
		"access_token_key": os.environ.get("SCOVID_TWITTER_ACCESS_TOKEN"),
		"access_token_secret": os.environ.get("SCOVID_TWITTER_ACCESS_SECRET"),
	}

	vaccine = Vaccines()
	infections = Infections()

	auth = tweepy.OAuthHandler(
		twitter_keys["consumer_key"], twitter_keys["consumer_secret"]
	)
	auth.set_access_token(
		twitter_keys["access_token_key"], twitter_keys["access_token_secret"]
	)

	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	vaccine_data = vaccine.vaccines_daily()
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

	if dry_run:
		return f"--dry-run passed, would be tweeting the following message:\n{text.format(**v)}"

	try:
		api.update_status(text.format(**v))
	except tweepy.RateLimitError as e:
		tweet_logger.error("Error: " + e.response.text)
		sys.exit(1)
	except tweepy.TweepError as e:
		tweet_logger.error("Error: " + e.response.text)
		sys.exit(1)
	except:
		tweet_logger.error("Unknown Error.")
		sys.exit(1)


if __name__ == "__main__":
	dry_run = "--dry-run" in sys.argv
	print(main(dry_run))
