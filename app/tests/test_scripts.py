"""
Tests for scovid19.scripts using pytest
"""

from app.scripts.tweet import main as tweet


class TestTweet:
    def test_tweet(self):
        tweet_result = tweet(dry_run=True)
        assert "would be tweeting" in tweet_result
