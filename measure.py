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
from datetime import timedelta
# errors!
import error_messenger
# sleep is important
import time
# import the sentiment analysis
from sentiment_analyzer import SentimentAnalyzer
from sentiment_classification import SentimentClassification
# we need to convert a dictionary to a json string
import json


# OK. We will store every incoming tweet (excluding those that are RTs and such) in the raw data json
# We will also do some minor analysis of the data, such as (per day) counting:
# 0. day 1. offensiveness freq, 2. neutral freq, 3. kind freq, 4. combined score, 5. total freq
# The processed data, then, will not be using the probability distributions –  only the most likely classification
# Thus, it should be interpreted with caution: it is not very reliable data. It should be used as a first sign, an indication of the results, and not the results themselves
# The combined score is calculated by assigning -1 to offensive tweets, 0 to neutral tweets, and 1 to kind tweets


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


# the data, resetted each day
hate_speech_frequency = 0
offensive_but_not_hate_speech_frequency = 0
not_offensive_frequency = 0
# the combined score increases by 2 when a hate speech tweet is encountered, and by 1 when an only offensive tweet is found
combined_score = 0
total_frequency = 0


# The main function, taking control of everything
def main():
    # do some setup
    set_up()
    # we will have two threads.
    # one will be the streamer thread, which continuously gathers tweets from the users, and outputs them to the raw file
    # the streamer also analyzes the tweet text for sentiment, and increases the appropriate tally
    # the other thread will be a day-long loop, which stores the information in the running tallies in the processed data file
    # it then resets the tallies
    streamer_thread = Thread(target = tweet_streamer)
    process_data_thread = Thread(target = process_data_loop)
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
    global user_ids
    streamer_object = TweetStreamer(setup.MEASURING_CONSUMER_KEY, setup.MEASURING_CONSUMER_SECRET, setup.MEASURING_ACCESS_TOKEN, setup.MEASURING_ACCESS_TOKEN_SECRET)
    # for error logs
    streamer_object.arvid220u_error_title = "measure.py > tweet_streamer()"
    # add the observer (the new_mention method)
    streamer_object.arvid220u_add_observer(new_tweet)
    # start streaming
    
    while not self_destruction_flag:
        try:
            # RTs will automatically be discarded (default setting)
            # check for tweets written by any of the user ids in our follow list
            streamer_object.statuses.filter(follow = user_ids)
        except Exception as exception:
            if self_destruction_flag:
                break
            # check if error is incomplete read; then just continue
            """if str(exception) == "('Connection broken: IncompleteRead(0 bytes read, 1 more expected)', IncompleteRead(0 bytes read, 1 more expected))":
                continue
            if str(exception) == "('Connection broken: IncompleteRead(0 bytes read, 2 more expected)', IncompleteRead(0 bytes read, 2 more expected))":
                continue"""
            if str(exception).startswith("('Connection broken: IncompleteRead"):
                print("restarting")
                continue
            # oh no! an error occurred
            # this is not good. not good at all. we don't want the measuring process to have a hole in it
            # we want complete data.
            # thus, try immediately with the backup twitter app
            print("measure.py > tweet_streamer(): ")
            print(exception)
            error_messenger.send_error_message(exception, "measure.py > tweet_streamer()")
            error_messenger.send_error_message("Starting backup measuring app. Not good.", "measure.py > tweet_streamer()")

            try:
                # reinitialize the streamer object
                streamer_object = TweetStreamer(setup.MEASURING_BACKUP_CONSUMER_KEY, setup.MEASURING_BACKUP_CONSUMER_SECRET, setup.MEASURING_BACKUP_ACCESS_TOKEN, setup.MEASURING_BACKUP_ACCESS_TOKEN_SECRET)
                # for error logs
                streamer_object.arvid220u_error_title = "measure.py > tweet_streamer()"
                # add the observer (the new_mention method)
                streamer_object.arvid220u_add_observer(new_tweet)
                # try again, same thing
                # if it fails this time, then i don't know what to do
                streamer_object.statuses.filter(follow = user_ids)
            except Exception as exception:
                if self_destruction_flag:
                    continue
                # well
                # nothing to do, I guess
                # beyond sending error messages, sleeping for an hour, and hoping for the best
                print("measure.py > tweet_streamer(): ")
                print(exception)
                print("CRITICAL. BACKUP FAILED.")
                error_messenger.send_error_message(exception, "measure.py > tweet_streamer()")
                error_messenger.send_error_message("CRITICAL. BACKUP MEASURING BOT FAILED. Will now sleep for five minutes.", "measure.py > tweet_streamer()")
                time.sleep(5*60)


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
    global sentiment_analyzer
    global hate_speech_frequency
    global offensive_but_not_hate_speech_frequency
    global not_offensive_frequency
    global combined_score
    global total_frequency
    print("new tweet")
    # simply print this tweet's json string to the raw data (along with an appended comma)
    # also analyze it for sentiment, and increment the appropriate day tallies
    # start by writing the content to the raw file
    with open(setup.RAW_DATA_PATH, "a") as raw_file:
        raw_file.write(json.dumps(tweet))
        raw_file.write(",")
    # analyze the sentiment
    sentiment_verdict = sentiment_analyzer.analyze_tweet_verdict(tweet["text"])
    # increment the total tally
    total_frequency += 1
    # update the respective frequency
    if sentiment_verdict == SentimentClassification.hate_speech:
        hate_speech_frequency += 1
        combined_score += 2
    elif sentiment_verdict == SentimentClassification.offensive_but_not_hate_speech:
        offensive_but_not_hate_speech_frequency += 1
        combined_score += 1
    elif sentiment_verdict == SentimentClassification.not_offensive:
        not_offensive_frequency += 1



# a 24-hour-long loop collecting the data
def process_data_loop():
    global hate_speech_frequency
    global offensive_but_not_hate_speech_frequency
    global not_offensive_frequency
    global combined_score
    global total_frequency
    # this loop should run continuously, until the self destruct flag is set
    # the last recorded time
    last_time = datetime.utcnow()
    while not self_destruction_flag:
        # start with a sleep, until exactly 24 hours has passed since the last_time
        next_time = last_time + timedelta(seconds = 24*60*60)
        time.sleep((next_time - datetime.utcnow()).total_seconds())
        if self_destruction_flag:
            break
        # write the current variables to the processed file
        with open(setup.PROCESSED_DATA_PATH, "a") as processed_file:
            processed_file.write(str(next_time) + ",")
            processed_file.write(str(hate_speech_frequency) + "," + str(offensive_but_not_hate_speech_frequency) + "," + str(not_offensive_frequency) + "," + str(combined_score) + "," + str(total_frequency))
            processed_file.write("\n")
        # reset the variables
        hate_speech_frequency = 0
        offensive_but_not_hate_speech_frequency = 0
        not_offensive_frequency = 0
        combined_score = 0
        total_frequency = 0
        # last time is next time
        last_time = next_time



def set_up():
    # before doing anything else, initialize the sentiment analyzer
    global sentiment_analyzer
    sentiment_analyzer = SentimentAnalyzer()
    print("initialized sentiment analyzer")

    # first check to see whether or not the data files are empty or not
    # if they are nonempty, then notify, and quit
    if is_non_zero_file(setup.RAW_DATA_PATH) or is_non_zero_file(setup.PROCESSED_DATA_PATH):
        print("Data already exists, either at " + setup.RAW_DATA_PATH + " or at " + setup.PROCESSED_DATA_PATH + ".")
        print("Delete these files (after having copied its contents, perhaps), and try again.")
        print("Measure.py will now self destruct.")
        import sys
        sys.exit()
    # Set up the two data files
    # the raw data file should be in json format
    # thus, write to it an square bracket
    with open(setup.RAW_DATA_PATH, "w") as raw_file:
        raw_file.write("[")
    # the processed data file should be a csv file
    with open(setup.PROCESSED_DATA_PATH, "w") as processed_file:
        processed_file.write("Date,Hate Speech Tally,Offensive But Not Hate Speech Tally,Not Offensive Tally,Combined Score,Total Tally\n")
    # load the user ids
    global user_ids
    with open(setup.USER_IDS_PATH, "r") as user_ids_file:
        for line in user_ids_file:
            sml = [x for x in line.strip().split()]
            user_id = int(sml[0])
            user_ids.append(user_id)
    # that's about it



# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
    main()
