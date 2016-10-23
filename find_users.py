#!/usr/bin/env python3

# Run this script to find users, and add them to the user ids text file
# Don't run find_users and either of the measure and tweet simultaneously


import setup
# import threading
from threading import Thread
# import the sentiment analysis


# How to do this?
# Hmm... Maybe, I should just stream random tweets, and find ones with a threshold sufficiently high?
# Perhaps the user ids should be stored in sort of a priority queue
# In that case, no specific threshold needs to be set; instead, the list of users just keeps getting better over time
# To make the process easier and to be able to update the code whilst running, implement some sort of command for saving and aborting
# e.g. 'q', which saves the users to the user_ids.txt file, along with their hatefulness score (the priority queue rank, of sorts)
# I guess it is very important for the sentiment analysis to be correct – everything builds upon it


# since number of users in this implementation only is 1000, then don't care about priority queues
# the number of users will never exceed a million, since that'd be unfeasible, which means that running an O(n) operation...
# ...for finding the minimum value in a simple list, won't prove to be a bottleneck in any way
# format: tuple of (user_id, hatefulness_score)
# the hatefulness score is simply the ratio between a user's hateful tweets and all his/her tweets
user_ids = []


def main():
    # define two threads: one user_abort, and one setup_streamer (which also, incidentally, starts the streamer)
    abort_thread = Thread(target = user_abort)
    streamer_thread = Thread(target = setup_streamer)
    # start them both
    abort_thread.start()
    streamer_thread.start()


def user_abort():
    def save_user_ids():
        global user_ids
        # save the user_ids list into the user_ids.txt file
        # completely overwrite the file, since user_ids should contain all entries already in it
        # do it atomically (nah, seems to complex for a tiny benefit)
        with open(setup.USER_IDS_PATH, "w") as user_ids_file:
            for (user_id, hatefulness_score) in user_ids:
                user_ids_file.write(str(user_id) + " " + str(hatefulness_score) + "\n")
        print("saved user ids to " + setup.USER_IDS_PATH)
    # listen for user abort
    while True:
        user_response = input()
        if (user_response == "q"):
            # now quit
            global streamer
            steamer.disconnect()
            # save user ids
            save_user_ids()
            # sys exit
            import sys
            sys.exit()
        elif (user_response == "w"):
            save_user_ids()
        else:
            print("Type 'q' to exit and save, and 'w' to save without quitting. Don't use ^C, as it won't save any data gathered since last save.")
            continue



def setup_streamer():
    # make the streamer global, so as to be able to access it in the user abort function
    global streamer
    # use the tweeting app
    streamer = TweetStreamer(setup.TWEETING_CONSUMER_KEY, setup.TWEETING_CONSUMER_SECRET, setup.TWEETING_ACCESS_TOKEN, setup.TWEETING_ACCESS_TOKEN_SECRET)
    # for error logs
    streamer.arvid220u_error_title = "find_users.py"
    # add the observer (the new_tweet method)
    streamer.arvid220u_add_observer(new_tweet)
    # start streaming
    # the track keyword is interesting. perhaps, if the search phrase is the same as the train search phrase, results will be skewed, in a bad way
    streamer.statuses.filter(track=setup.SEARCH_PHRASE, language=setup.LANGUAGE)



# Return a float in the interval [0, 1], which represents the ratio of hateful tweets
# Disregard both kind and neutral tweets, since they are here deemed to have no impact
def score_user(user_id):
    print("score user")


def new_tweet(tweet):
    # only proceed to score the user if this tweet is classified as hateful
    print("new tweet")




# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
    main()
