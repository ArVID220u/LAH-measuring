#!/usr/bin/env python3

# the TweetStreamer is a subclass of TwythonStreamer
from twython import TwythonStreamer
# errors!
import error_messenger

# the TweetStreamer class will use the streaming api to check for new tweets.
# It will be used for filtering all tweets containing the trigger word specified in setup.py
# This class could technically be used to reply to all kinds of tweets.
class TweetStreamer(TwythonStreamer):

    # Simple label to know from where the tweet streamer was called
    arvid220u_error_title = "placeholder"

    # Normally, retweets should be excluded
    arvid220u_exclude_retweets = True

    arvid220u_new_tweet_observers = []

    def arvid220u_add_observer(self, observer):
        self.arvid220u_new_tweet_observers.append(observer)

    # this function will be called when a tweet is received
    def on_success(self, data):
        if "text" not in data:
            return
        if self.arvid220u_exclude_retweets:
            # filter out retweets
            if data["text"].startswith("RT"):
                return
            if "retweeted_status" in data:
                return
        # send tweet to the specified delegate function
        # self.new_tweet needs to be set
        for observer in self.arvid220u_new_tweet_observers:
            observer(data)

    # when an error is caught
    def on_error(self, status_code, data):
        print("STREAMING API ERROR IN TWEETSTREAMER!")
        print("Status code:")
        print(status_code)
        error_messenger.send_error_message("streaming API error, with code " + str(status_code), "TweetStreamer.on_error from " + arvid220u_error_title)
        print("Other data:")
        print(data)
        print("END OF ERROR MESSAGE")

    # on timeout
    def on_timeout(self):
        print("STREAMING API TIMEOUT IN TWEETSTREAMER!")
        error_messenger.send_error_message("streaming API timeout", "TweetStreamer.on_timeout from " + arvid220u_error_title)
        print("END OF ERROR MESSAGE")
