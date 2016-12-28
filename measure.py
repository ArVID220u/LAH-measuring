#!/usr/bin/env python3

# The measuring main script
# Run this script ("./measure.py") to start the measuring process
# It is based on the user id text file


# twitter API
import twythonaccess
from twythonaccess import TwitterApp
# import the streamer
from streamer import TweetStreamer
# import setup
import setup
# import threading
from threading import Thread
# import datetime
from datetime import datetime
# errors!
import error_messenger


# OK. We will store every incoming tweet (excluding those that are RTs and such) in the raw data json
# We will also do some minor analysis of the data, such as (per day) counting:
# 0. day 1. offensiveness freq, 2. neutral freq, 3. kind freq, 4. combined score, 5. total freq
# The processed data, then, will not be using the probability distributions –  only the most likely classification
# Thus, it should be interpreted with caution: it is not very reliable data. It should be used as a first sign, an indication of the results, and not the results themselves


# a simple function for checking whether the specified file path is empty or not
import os
def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0



# the streamer. a global needed so as to be able to disconnect it
streamer_object = None


# the flag for self destruction
self_destruction_flag = False


# a list of user_ids
user_ids = []


# The main function, taking control of everything
def main():
    # first check to see whether or not the data files are empty or not
    # if they are nonempty, then notify, and quit
    if is_non_zero_file(setup.RAW_DATA_PATH) || is_non_zero_file(setup.PROCESSED_DATA_PATH):
        print("Data already exists, either at " + setup.RAW_DATA_PATH + " or at " + setup.PROCESSED_DATA_PATH + ".")
        print("Delete these files (after having copied its contents, perhaps), and try again.")
        print("Measure.py will now self destruct.")
        import sys
        sys.exit()
    # do some setup
    setup()
    # we will have two threads.
    # one will be the streamer thread, which continuously gathers tweets from the users, and outputs them to the raw file
    # the streamer also analyzes the tweet text for sentiment, and increases the appropriate tally
    # the other thread will be a day-long loop, which stores the information in the running tallies in the processed data file
    # it then resets the tallies
    streamer_thread = Thread(target = tweet_streamer)
    process_data_thread = Thread(target = process_data_thread)
    # start the threads
    streamer_thread.start()
    process_data_thread.start()
    



# destruct self
# a call will end the measuring process, and clean up the data files (e.g. fixing the json format in the raw file)
def self_destruct():
    print("self destruct")
    # set the self desctruction flag, which will be used to terminate the process data loop as well as the streamer thread, in a safe way
    global self_destruction_flag
    self_destruction_flag = True
    # disconnect the streamer
    global streamer_object
    streamer_object.disconnect()
    # that's about it
    # the raw data file will be fixed in the streamer thread, to make the ending as graceful as possible




# the setting up streamer function
def tweet_streamer():
    print("tweet streamer")

    # set up the streamer
    # use the measuring app
    global streamer_object
    streamer_object = TweetStreamer(setup.MEASURING_CONSUMER_KEY, setup.MEASURING_CONSUMER_SECRET, setup.MEASURING_ACCESS_TOKEN, setup.MEASURING_ACCESS_TOKEN_SECRET)
    # for error logs
    mentions_streamer.arvid220u_error_title = "measure.py > tweet_streamer()"
    # add the observer (the new_mention method)
    streamer.arvid220u_add_observer(new_tweet)
    # start streaming
    
    while not self_destruction_flag:
        # start the filtering, with error handling

    # now, we have finished streaming, and are probably in the self destruct phase
    # end the json by removing the last character (the comma) and subsituting it for a closed square bracket
    with open(setup.RAW_DATA_PATH, 'rb+') as filehandle:
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
    # subsitute it for the closed square bracket
    with open(setup.RAW_DATA_PATH, "a") as raw_file:
        raw_file.write("]")



# this method is called once for every new tweet from the streamer
def new_tweet(tweet):
    print("new tweet")



# a 24-hour-long loop collecting the data
def process_data_loop():
    print("process data loop")


def setup():
    # Set up the two data files
    # the raw data file should be in json format
    # thus, write to it an square bracket
    with open(setup.RAW_DATA_PATH, "w") as raw_file:
        raw_file.write("[")
    # the processed data file should be a csv file
    with open(setup.PROCESSED_DATA_PATH, "w") as processed_file:
        processed_file.write("Date,Offensive Tally,Neutral Tally,Kind Tally,Combined Score,Total Tally\n")
    # load the user ids
    global user_ids
    with open(setup.USER_IDS_PATH, "r") as user_ids_file:
        for line in user_ids_file:
            user_id, hatefulness_score = [int(x) for x in line.strip().split()]
            user_ids.append(user_id)
    # that's about it



# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
    main()
