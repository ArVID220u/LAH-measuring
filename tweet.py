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
# for shuffling the user ids list
import random
# we need to be able to sleep
import time


# the unscrambled list of user ids, as loaded directly from the user id text file
user_ids = []
# this is a dictionary containing the screen name for every user id
screen_name_for_user_id = {}

# a dictionary of user_id -> sent responses, so as to not send the same response to the same user twice
# thus, dict<int, set<string>>, as expressed in some pseudo-c++ syntax (set instead of list?)
# remember that, if this process is run for a long time, you may run out of responses. thus, be sure to reset the list of taken responses when it has the same length as the responses list itself
sent_responses_to_user = {}

# a list of the responses, as loaded directly from the responses.txt text file
# (consequently, one cannot simply update the responses text file to make the bot send the new responses – this process needs to be restarted as well)
responses = []


# When this flag is set to true, all processes and threads should ideally stop executing
self_destruction_flag = False


# we need the mentions streamer as a global, so as to be able to disconnect it gracefully at self destruction
mentions_streamer_object = None



# The main function, which should start both the mentions streamer and the tweet loop
def main():
    print("main")
    # setup is important
    set_up()
    print("setup done")
    # one thread should be the mentions streamer
    mentions_thread = Thread(target = mentions_streamer)
    # one thread should be the tweet loop
    tweet_loop_thread = Thread(target = tweet_loop)
    # start the threads
    mentions_thread.start()
    tweet_loop_thread.start()



# We need a way to self destruct ourselves, so as to be able to stop sending tweets
def self_destruct():
    # First, set the self destruction flag to true
    global self_destruction_flag
    self_destruction_flag = True
    # Then, disconnect the mentions streamer
    global mentions_streamer_object
    mentions_streamer_object.disconnect()




def set_up():
    # do some setup first, like loading the user ids into a list, 
    # and also create the dictionary of user ids to sent responses
    # finally, load the list of responses from the responses text file, for easy access

    # load the user ids
    global user_ids
    with open(setup.USER_IDS_PATH, "r") as user_ids_file:
        for line in user_ids_file:
            sml = [x for x in line.strip().split()]
            user_id = int(sml[0])
            user_ids.append(user_id)

    # find the screen name for every user id
    global screen_name_for_user_id
    # if we can't get the screen name, then something's wrong
    # add that user to the remove queue
    remove_list = []
    for user_id in user_ids:
        # use the mentions app for checking up the user
        # this is since it is less critical than the tweeting app, while having the same privileges
        # if rate limited, wait for 1 minute, and then try again
        # the show user request can be sent 900 times per 15 minute window
        while twythonaccess.currently_rate_limited(TwitterApp.mentions, 900):
            time.sleep(60)
        # get the screen name of the user
        try:
            screen_name = twythonaccess.authorize(TwitterApp.mentions).show_user(user_id = user_id)["screen_name"]
            screen_name_for_user_id[user_id] = screen_name
        except Exception as exception:
            # can't find screen name of this user
            print(exception)
            remove_list.append(user_id)
            print("Can't find screen name of user with id: " + str(user_id))
    error_messenger.send_error_message("Removing " + str(len(remove_list)) + " users due to inability to get their screen name.", "tweet.py > set_up()")
    for user_id in remove_list:
        user_ids.remove(user_id)

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
    global mentions_streamer_object
    mentions_streamer_object = TweetStreamer(setup.MENTIONS_CONSUMER_KEY, setup.MENTIONS_CONSUMER_SECRET, setup.MENTIONS_ACCESS_TOKEN, setup.MENTIONS_ACCESS_TOKEN_SECRET)
    # for error logs
    mentions_streamer_object.arvid220u_error_title = "tweet.py > mentions_streamer()"
    # add the observer (the new_mention method)
    mentions_streamer_object.arvid220u_add_observer(new_mention)
    # start streaming
    # wrap it in error handling
    while not self_destruction_flag:
        try:
            # RTs will automatically be discarded (default setting)
            # check for tweets referencing self
            mentions_streamer_object.statuses.filter(track=("@" + setup.TWITTER_USERNAME))
        except Exception as exception:
            # If self destruction flag is true, then continue (same as break)
            if self_destruction_flag:
                break
            # check if exception is incomplete read: then, just restart immediately
            """if str(exception) == "('Connection broken: IncompleteRead(0 bytes read, 1 more expected)', IncompleteRead(0 bytes read, 1 more expected))":
                continue
            if str(exception) == "('Connection broken: IncompleteRead(0 bytes read, 2 more expected)', IncompleteRead(0 bytes read, 2 more expected))":
                continue"""
            if str(exception).startswith("('Connection broken: IncompleteRead"):
                print("restarting")
                continue
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
    # if the self desturction flag is on, then return immediately
    if self_destruction_flag:
        return

    # first check so that the user actually did mention the bot
    did_mention = False
    for user_mention in tweet["entities"]["user_mentions"]:
        if user_mention["screen_name"] == setup.TWITTER_USERNAME:
            did_mention = True
    if not did_mention:
        # return early if no mention
        # it's strange that this can happen
        return


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
    reply_to_screen_name = tweet["user"]["screen_name"]
    # create the tweet
    reply_tweet = "@" + reply_to_screen_name + " " + setup.REPLY_TWEET
    # send the tweet, and check whether it was actually sent
    if twythonaccess.send_tweet(reply_tweet, TwitterApp.mentions, in_reply_to_status_id = tweet["id"]):
        # yay, tweet was sent
        # now add this user to the replied to users map, along with the current timestamp
        replied_to_users[user_id] = datetime.utcnow()



# The tweet loop runs indefinitely, sending one tweet per week per user, at a randomly assigned time.
# Needs thorough error handling.
# If an error occurs here, a lot is lost on the experiment
# Therefore, immediately retry a couple of times upon receiving the error
def tweet_loop():
    global user_ids
    global sent_responses_to_user
    global responses
    global screen_name_for_user_id
    print("tweet loop")
    # have an infinte loop
    # every loop iteration should take one week, and in each iteration, exactly one tweet should be sent to each user
    while not self_destruction_flag:
        start_time = datetime.utcnow()
        # first, scramble the user ids list so as to make the sending of the users completely random
        user_ids_sendlist = user_ids[:]
        random.shuffle(user_ids_sendlist)
        # calculate the interval, so as to make the loop week-long
        # we do care about achieving perfect week-loops, which is why we make the interval a tiny bit shorter (one hour) than actually needed, and storing the starting time
        # (the reason we care is for measuring purposes, and credibility in statistics, etc)
        # the tweet interval is measured in seconds
        tweet_interval = ((7*24*60*60-60*60) / len(user_ids))
        # now iterate over each user id in the sendlist
        for user_id in user_ids_sendlist:
            # if we are in self destruction, then return here (and yes, I know, it may be that not all users receive the same amount of tweets, this way)
            # (continuing thought: but it is of utter importance to have the treatment stop at the given signal)
            if self_destruction_flag:
                break
            # randomly choose a tweet from the response list
            # do it repeatedly until a response that has not yet been sent to this user is found
            # first, check whether the response set for this user has a length that is equal to the response list – if so, reset it
            if len(sent_responses_to_user[user_id]) >= len(responses):
                sent_responses_to_user[user_id] = set()
            response = responses[random.randint(0,len(responses)-1)]
            while response in sent_responses_to_user[user_id]:
                response = responses[random.randint(0,len(responses)-1)]
            # send this response to the user, mentioning them
            response_tweet = "@" + screen_name_for_user_id[user_id] + " " + response + " " + setup.RESPONSE_SUFFIX
            # send this tweet
            # don't care whether it is sent or not – as long as there are not too many users, it should be sent without any problem
            # risk is twitter banning the bot due to its messages being considered unsolicited and rude
            try:
                twythonaccess.send_tweet(response_tweet, TwitterApp.tweeting)
            except Exception as exception:
                # oh no! an error occured
                # well then. just sleep for sixteen minutes (we have one hour spare), and try once again. if it doesn't work this time, something's severly wrong
                print(exception)
                error_messenger.send_error_message(exception, "tweet.py > tweet_loop()")
                print("will sleep for twenty minutes to try to avoid the exception")
                time.sleep(16*60)
                print("has slept for twenty minutes and will retry sending the tweet")
                if self_destruction_flag:
                    break
                try:
                    twythonaccess.send_tweet(response_tweet, TwitterApp.tweeting)
                except Exception as exception2:
                    # no no no no no!
                    # this is not where we want to end up
                    # switch to the backup tweeting app, by setting the twythonaccess backup mode to on
                    # also send an urgency error message, explaining what's happening
                    print(exception)
                    print("toggling backup mode in tweeting app")
                    twythonaccess.tweeting_in_backup_mode = not twythonaccess.tweeting_in_backup_mode
                    error_messenger.send_error_message("IMPORTANT: Tweeting app now toggled its backup mode", "tweet.py > tweet_loop()")
                    try:
                        twythonaccess.send_tweet(response_tweet, TwitterApp.tweeting)
                    except Exception as exception3:
                        # i have no idea what to do by now. probably, just shut the whole thing down
                        # we're doomed if we reach this point
                        # goodbye, world
                        print(exception)
                        error_messenger.send_error_message(exception, "tweet.py > tweet_loop()")
                        error_messenger.send_error_message("We're all doomed. Exception couldn't be resolved, even after tremendous effort. Now, ignoring the error.", "tweet.py > tweet_loop()")
            # add the chosen response to the sent responses set
            sent_responses_to_user[user_id].add(response)
            # now, sleep for the specified interval
            time.sleep(tweet_interval)
        # great. all users have been addressed
        # now, sleep until exactly one week has passed since the start time
        while (datetime.utcnow() - start_time).total_seconds() <= 7*24*60*60:
            time.sleep(1)


# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
    main()
