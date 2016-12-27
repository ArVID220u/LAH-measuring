# This module provides the api twython object, which is used to access the api

# import datetime
from datetime import datetime

# Import twython
from twython import Twython

# import the api keys from setup
import setup

# import enum for the different apps
# Requires python 3.4?
from enum import Enum



# an enum representing the four different apps
class TwitterApp(Enum):
    tweeting = 1
    mentions = 2
    measuring = 3
    error_messenger = 5

# Store the timestamps for the last requests, for each bot
last_requests_timestamps = {twitter_app: [] for twitter_app in TwitterApp}


# Since the operations of the bot are crucial, and we constantly run a risk of getting restricted by the Twitter API, have two backup apps
# The two crucial operations are tweeting and measuring, so we only have backups for them
tweeting_in_backup_mode = False
measuring_in_backup_mode = False



# the twitter_app parameter is a TwitterApp enum
# only the mentions app needs to be rate limit checked, since the others manage that themselves
def authorize(twitter_app):
    global last_requests_timestamps
    # add the current time the the last request timestamps
    last_requests_timestamps[twitter_app].append(datetime.utcnow())
    # authorization for each bot
    if twitter_app == TwitterApp.tweeting:
        # authorize
        # choose different keys based on whether backup mode is on or not
        if not tweeting_in_backup_mode:
            return Twython(setup.TWEETING_CONSUMER_KEY, setup.TWEETING_CONSUMER_SECRET, setup.TWEETING_ACCESS_TOKEN, setup.TWEETING_ACCESS_TOKEN_SECRET)
        else:
            return Twython(setup.TWEETING_BACKUP_CONSUMER_KEY, setup.TWEETING_BACKUP_CONSUMER_SECRET, setup.TWEETING_BACKUP_ACCESS_TOKEN, setup.TWEETING_BACKUP_ACCESS_TOKEN_SECRET)
    elif twitter_app == TwitterApp.measuring:
        # authorize
        # choose differnet keys based on whether backup mode is on or not
        if not tweeting_in_backup_mode:
            return Twython(setup.MEASURING_CONSUMER_KEY, setup.MEASURING_CONSUMER_SECRET, setup.MEASURING_ACCESS_TOKEN, setup.MEASURING_ACCESS_TOKEN_SECRET)
        else:
            return Twython(setup.MEASURING_BACKUP_CONSUMER_KEY, setup.MEASURING_BACKUP_CONSUMER_SECRET, setup.MEASURING_BACKUP_ACCESS_TOKEN, setup.MEASURING_BACKUP_ACCESS_TOKEN_SECRET)
    elif twitter_app == TwitterApp.mentions:
        # authorize
        return Twython(setup.MENTIONS_CONSUMER_KEY, setup.MENTIONS_CONSUMER_SECRET, setup.MENTIONS_ACCESS_TOKEN, setup.MENTIONS_ACCESS_TOKEN_SECRET)
    elif twitter_app == TwitterApp.error_messenger:
        # authorize
        return Twython(setup.ERROR_MESSAGE_CONSUMER_KEY, setup.ERROR_MESSAGE_CONSUMER_SECRET, setup.ERROR_MESSAGE_ACCESS_TOKEN, setup.ERROR_MESSAGE_ACCESS_TOKEN_SECRET)


# This function returns a bool indicating whether or not the specified app is currently rate limited or not (that is, having sent exactly X requests the last 15 minutes)
# (Here, X is typically either 180 or 15)
# Note that while Twitter seems to count rate limits for each API method individually, this method does not do that. The effect being that the bot sleeps too much, if one likes to put it that way.
def currently_rate_limited(twitter_app, limit):
    global last_requests_timestamps
    # get now time
    now_time = datetime.utcnow()
    # first filter out each tweet that is older than 15 minutes
    # use 16 minutes instead of 15 to have a safety margin
    last_requests_timestamps[twitter_app] = [tweet_time for tweet_time in last_requests_timestamps[twitter_app] if (now_time - tweet_time).total_seconds() < 16*60]
    # check if length is greater than or equal to limit: then we must wait. (greater than should never happen, but include it in any case)
    return len(last_requests_timestamps[twitter_app]) >= limit


# this method sends a tweet
# it returns true if successful, and false if not
def send_tweet(tweet, twitter_app, in_reply_to_status_id=0):

    if len(tweet) > 140:
        print("too long tweet, not sending it")
        return False


    # simply don't send tweet if the app is currently rate limited
    # return false, indicating that no tweet was sent
    if currently_rate_limited(twitter_app, 15):
        # print error message
        print("rate limited in " + twitter_app + " when trying to send tweet: " + tweet)
        print("returning prematurely and silently")
        return False

    # maybe send it in reply to another tweet
    if in_reply_to_status_id == 0:
        # standalone tweet
        authorize(twitter_app).update_status(status=tweet)
    else:
        # tweet is a reply
        authorize(twitter_app).update_status(status=tweet, in_reply_to_status_id=in_reply_to_status_id)
    print("sent tweet: " + tweet)
    return True
