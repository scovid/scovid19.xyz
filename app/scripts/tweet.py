#!/usr/bin/env python3

import os
import sys
import tweepy
from datetime import datetime
from app.lib.data.Vaccines import Vaccines
from app.lib.data.Infections import Infections
from app.lib.Util import get_logger


def main(dry_run=False):
    # Disable caching to always pull latest stats
    os.environ["SCOVID_NO_CACHE"] = "1"

    tweet_logger = get_logger("tweet_bot")

    vaccine = Vaccines()
    infections = Infections()

    vaccine_data = vaccine.summary()
    infection_data = infections.summary()

    daily_cases = f"{infection_data['cases']['new']:,.0f}"

    date = datetime.today().strftime("%Y-%m-%d")

    v = {
        "date": date,
        "dose1": f"{vaccine_data['totals']['Dose 1']:,.0f}",
        "dose2": f"{vaccine_data['totals']['Dose 2']:,.0f}",
        "daily_cases": daily_cases,
    }
    text = "Scotland vaccinations as of 08:30am on {date}: \n\n First Dose: {dose1} \n Second Dose: {dose2} \n\n {daily_cases} new cases reported \n\n For more stats visit www.scovid19.xyz"

    if dry_run:
        return f"--dry-run passed, would be tweeting the following message:\n{text.format(**v)}"

    try:
        send_tweet(text.format(**v))
    except tweepy.RateLimitError as e:
        tweet_logger.error(f"RateLimitError: {e}")
        sys.exit(1)
    except tweepy.TweepError as e:
        tweet_logger.error(f"TweepError: {e}")
        sys.exit(1)
    except Exception as e:
        tweet_logger.error(f"Error: {e}")
        sys.exit(1)


def send_tweet(msg: str):
    """
    Authentice via twitter API and send the tweet
    """

    twitter_keys = {
        "consumer_key": os.environ.get("SCOVID_TWITTER_API_KEY"),
        "consumer_secret": os.environ.get("SCOVID_TWITTER_API_SECRET"),
        "access_token_key": os.environ.get("SCOVID_TWITTER_ACCESS_TOKEN"),
        "access_token_secret": os.environ.get("SCOVID_TWITTER_ACCESS_SECRET"),
    }

    auth = tweepy.OAuthHandler(
        twitter_keys["consumer_key"], twitter_keys["consumer_secret"]
    )
    auth.set_access_token(
        twitter_keys["access_token_key"], twitter_keys["access_token_secret"]
    )

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    api.update_status(msg)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    print(main(dry_run))
