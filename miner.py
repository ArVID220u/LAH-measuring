# the Miner class is a subclass of TwythonStreamer
from twython import TwythonStreamer

# the Miner class will use the streaming api to check for new tweets.
# It will be used for filtering all tweets from the test group.
class Miner(TwythonStreamer):

    # this function will be called when a tweet is received
    def on_success(self, data):
        # send tweet to the organizer, which should process the tweet and send it for analysis
        self.organizer.add_tweet(data)

    # when an error is caught
    def on_error(self, status_code, data):
        print("STREAMING API ERROR IN ALLSWEDISHSTREAMER!")
        print("Status code:")
        print(status_code)
        print("Other data:")
        print(data)
        print("END OF ERROR MESSAGE")
