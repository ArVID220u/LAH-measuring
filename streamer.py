#!/usr/bin/env python3

# the TweetStreamer is a subclass of TwythonStreamer
from twython import TwythonStreamer
# errors!
from error_messenger import send_error_message

# the TweetStreamer class will use the streaming api to check for new tweets.
# It will be used for filtering all tweets containing the trigger word specified in setup.py
# This class could technically be used to reply to all kinds of tweets.
class TweetStreamer(TwythonStreamer):

    # Simple label to know from where the tweet streamer was called
    error_title = "placeholder"

    new_tweet_observers = []

    def add_observer(self, observer):
        self.new_tweet_observers.append(observer)

    # this function will be called when a tweet is received
    def on_success(self, data):
        # send tweet to the specified delegate function
        # self.new_tweet needs to be set
        for observer in self.new_tweet_observers:
            observer(data)

    # when an error is caught
    def on_error(self, status_code, data):
        print("STREAMING API ERROR IN TWEETSTREAMER!")
        print("Status code:")
        print(status_code)
        send_error_message("streaming API error, with code " + str(status_code), "TweetStreamer.on_error from " + error_title)
        print("Other data:")
        print(data)
        print("END OF ERROR MESSAGE")
