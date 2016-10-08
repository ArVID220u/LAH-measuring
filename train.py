#!/usr/bin/env python3

# Run this script for a simple way to train the sentiment analyzer
# Stream random tweets and send them to the sentiment_database
# Never run this simultaneously with any other function of LAH (especially not find_users or tweet)

# import setup
import setup
# import the sentiment database
import sentiment_database
# import the streamer
from streamer import TweetStreamer
# import random
import random

# Initialize a streamer, and set the callback to sentiment_database's add_tweet
def main():
    # use the tweeting app
    streamer = TweetStreamer(setup.TWEETING_CONSUMER_KEY, setup.TWEETING_CONSUMER_SECRET, setup.TWEETING_ACCESS_TOKEN, setup.TWEETING_ACCESS_TOKEN_SECRET)
    # add the observer
    streamer.add_observer(get_tweet)
    # start streaming
    streamer.statuses.filter(track=setup.SEARCH_PHRASE, language=setup.LANGUAGE)

def get_tweet(tweet):
    if tweet["entities"]["urls"]:
        return
    if "you" not in tweet["text"]:
        return
    sentiment_database.add_tweet(tweet)


# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
    main()
