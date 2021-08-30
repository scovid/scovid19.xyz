"""
Tests for scovid19.scripts using pytest
Uses the responses module to return dummy data to http requests
The mock responses are stored in scovid19/tests/responses/
"""

import pytest
from app.lib.data import Scotland, Infections, Vaccines
from app.scripts.tweet import main as tweet


class TestTweet:
    def test_tweet(self):
        tweet_result = tweet(dry_run=True)
        assert "would be tweeting" in tweet_result
