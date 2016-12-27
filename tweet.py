#!/usr/bin/env python3

# Tweet at the users found in the user id text file (specified in setup.py)
# Not to be run simultaneously as the find_users.py script

# Also have a streamer that replies to replies

# OK, so what's the plan?
# I want to send people tweets at times when they tend to send their offensive tweets.
# This is to magnify the impact of the kind tweet.
# We really don't want the bot getting suspended for sending unsolicited tweets to people.
# Therefore, this procedure needs to be thoroughly scrutinized before launching the actual project.

# This is perhaps not very important. The timing, I mean.
# Rather, I should focus on getting the measurement correct, while still ensuring that each person gets sent one tweet a week.
# Thus, have a week-long loop. At start, it randomly scrambles the user id list, and at a set interval tweets to the users in the list's order.
# This will make the sending of the tweets truly random, and perfectly spread out (so as to minimize the risk of violating the API restrictions).


# import twythonaccess to be able to send tweets
import twythonaccess
from twythonaccess import TwitterApp
# import setup
import setup
# import the streamer
from streamer import TweetStreamer
# import threading
from threading import Thread
# import datetime
from datetime import datetime
# errors!
import error_messenger


# the unscrambled list of user ids, as loaded directly from the user id text file
user_ids = []

# a dictionary of user_id -> sent responses, so as to not send the same response to the same user twice
# thus, dict<int, set<string>>, as expressed in some pseudo-c++ syntax (set instead of list?)
# remember that, if this process is run for a long time, you may run out of responses. thus, be sure to reset the list of taken responses when it has the same length as the responses list itself
sent_responses_to_user = {}

# a list of the responses, as loaded directly from the responses.txt text file
# (consequently, one cannot simply update the responses text file to make the bot send the new responses – this process needs to be restarted as well)
responses = []



# The main function, which should start both the mentions streamer and the tweet loop
def main():
    print("main")
    # setup is important
    setup()
    print("setup done")
    # one thread should be the mentions streamer
    mentions_thread = Thread(target = mentions_streamer)
    # one thread should be the tweet loop
    tweet_loop_thread = Thread(target = tweet_loop)
    # start the threads
    mentions_thread.start()
    tweet_loop.start()


def setup():
    # do some setup first, like loading the user ids into a list, 
    # and also create the dictionary of user ids to sent responses
    # finally, load the list of responses from the responses text file, for easy access

    # load the user ids
    global user_ids
    with open(setup.USER_IDS_PATH, "r") as user_ids_file:
        for line in user_ids_file:
            user_id, hatefulness_score = [int(x) for x in line.strip().split()]
            user_ids.append(user_id)

    # create the dictionary of empty sets per each user id
    global sent_responses_to_user
    for user_id in user_ids:
        sent_responses_to_user[user_id] = set()

    # load the responses from the responses.txt file
    global responses
    with open(setup.RESPONSES_PATH, "r") as responses_file:
        for line in responses_file:
            response = line.strip()
            responses.append(response)




# Set up the mentions streamer, viz. the streamer that should find all tweets mentioning the bot, and reply to them with emoji hearts
# Runs indefinitely, and thus needs error handling
def mentions_streamer():
    print("mentions streamer")
    # initialize the mentions streamer
    # use the mentions app
    mentions_streamer = TweetStreamer(setup.MENTIONS_CONSUMER_KEY, setup.MENTIONS_CONSUMER_SECRET, setup.MENTIONS_ACCESS_TOKEN, setup.MENTIONS_ACCESS_TOKEN_SECRET)
    # for error logs
    mentions_streamer.arvid220u_error_title = "tweet.py > mentions_streamer()"
    # add the observer (the new_mention method)
    streamer.arvid220u_add_observer(new_mention)
    # start streaming
    # wrap it in error handling
    while True:
        try:
            # RTs will automatically be discarded (default setting)
            # check for tweets referencing self
            streamer.statuses.filter(track=("@" + setup.TWITTER_USERNAME))
        except Exception as exception:
            # print the exception and then sleep for an hour,
            # and hope that the problem will resolve itself, magically
            # (as it almost always does, since the problem is probably in Twitter's servers, or something)
            print("tweet.py > mentions_streamer(): ")
            print(exception)
            error_messenger.send_error_message(exception, "tweet.py > mentions_streamer()")
            print("will sleep for one hour to avoid exception")
            time.sleep(60*60)
            print("finished sleep in tweet.py > mentions_streamer. will now start anew")

            


# Map: user_id -> timestamp
# Timestamp records when the user with the id user_id was replied to
# This is to ensure that no more than a maximum of one reply per day is sent to one and the same user
replied_to_users = {}

# Whenever a new tweet referencing self is discovered, this method is called
# The argument is the ordinary tweet dictionary, as provided by twitter, without any changes
def new_mention(tweet):
    # hmm... Should it be possible for a user to be replied to many times, or should there be a limit on the number of responses per user?
    # This is interesting, though I'm not sure whether I know the perfect strategy.
    # Perhaps, the best way to go is to only reply once in a specified time range (say 1 day), instead of having it applied for all time
    # Yep, go with that.
    # Have a map: user_id -> timestamp.
    
    # the user to respond to
    user_id = tweet["user"]["id"]
    # check if that user is in the replied to users
    global replied_to_users
    if user_id in replied_to_users:
        # check whether the time passed since timestamp is less than one day
        now_time = datetime.utcnow()
        if (now_time - replied_to_users[user_id]).total_seconds() < 24*60*60:
            # simply return here, prematurely
            return
        # don't do anything. we will update the timestamp at a later stage

    # first check if the mentions app is currently rate limited, to later get its screen name
    # if it is rate limited, return silently, so as not to build up a queue here
    # Twitter allows 900 user shows per 15 minute window
    if twythonaccess.currently_rate_limited(TwitterApp.mentions, 900):
        # simply return silently
        return
    # get the screen name of the user to reply to
    reply_to_screen_name = twythonaccess.authorize(TwitterApp.mentions).show_user(user_id = user_id)["screen_name"]
    # create the tweet
    reply_tweet = "@" + reply_to_screen_name + " " + setup.REPLY_TWEET
    # send the tweet, and check whether it was actually sent
    if twythonaccess.send_tweet(reply_tweet, TwitterApp.mentions, in_reply_to_status_id = tweet["id"]):
        # yay, tweet was sent
        # now add this user to the replied to users map, along with the current timestamp
        replied_to_users[user_id] = datetime.utcnow()



# The tweet loop runs indefinitely, sending one tweet per week per user, at a randomly assigned time.
# Needs thorough error handling.
def tweet_loop():
    print("tweet loop")


# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
    main()
