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
# for the pairwise thing
from itertools import tee

# Initialize a streamer, and set the callback to sentiment_database's add_tweet
def main():
    # use the tweeting app
    streamer = TweetStreamer(setup.TWEETING_CONSUMER_KEY, setup.TWEETING_CONSUMER_SECRET, setup.TWEETING_ACCESS_TOKEN, setup.TWEETING_ACCESS_TOKEN_SECRET)
    # for error logs
    streamer.arvid220u_error_title = "main in train.py"
    # add the observer
    streamer.arvid220u_add_observer(get_tweet)
    # start streaming
    while True:
        try:
            streamer.statuses.filter(track=setup.TRAIN_PHRASE, language=setup.LANGUAGE)
        except:
            continue

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
def grouped(iterable):
    return zip(*[iter(iterable)]*2)

def BYB():
    with open("BYBnonabusivetweets.txt", "r") as f:
        x = f.read().split("%BOTYOURBACK||SPLIT%")
        x.pop()
        for a, b in grouped(x):
            i = {"text": a, "user": {"screen_name": b}, "id": b}
            sentiment_database.add_tweet(i)

def get_tweet(tweet):
    if tweet["entities"]["urls"]:
        return
    if "you" not in tweet["text"]:
        return
    sentiment_database.add_tweet(tweet)


# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
    main()
    #BYB()
