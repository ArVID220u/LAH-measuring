#!/usr/bin/env python3

# Run this script to find users, and add them to the user ids text file
# Don't run find_users and either of the measure and tweet simultaneously


import setup
# import threading
from threading import Thread
# import the sentiment analysis
from sentiment_analyzer import SentimentAnalyzer
from sentiment_analyzer import SentimentClassification
# import twythonaccess
import twythonaccess
from twythonaccess import TwitterApp
# import random for the simulations
import random
# import the streamer
from streamer import TweetStreamer


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
    # before doing anything else, initialize the sentiment analyzer
    global sentiment_analyzer
    sentiment_analyzer = SentimentAnalyzer()
    print("initialized sentiment analyzer")

    # also initialize the user ids array to all the elements currently in the user ids data file
    # first create the file
    open(setup.USER_IDS_PATH, "a").close()
    # then open it, and load all of its contents into the user_ids list
    global user_ids
    with open(setup.USER_IDS_PATH, "r") as user_ids_file:
        for line in user_ids_file:
            user_id, hatefulness_score = [int(x) for x in line.strip().split()]
            user_ids.append((user_id, hatefulness_score))

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
        # do it atomically (nah, seems too complex for a tiny benefit)
        with open(setup.USER_IDS_PATH, "w") as user_ids_file:
            for (user_id, hatefulness_score) in user_ids:
                user_ids_file.write(str(user_id) + " " + str(hatefulness_score) + "\n")
        print("saved user ids to " + setup.USER_IDS_PATH + ". Number of users: " + str(len(user_ids)))
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
    # 1. Create list of tweet texts
    user_tweets = twythonaccess.authorize(TwitterApp.tweeting).get_user_timeline(user_id = user_id, count = 200, trim_user = True, include_rts = False)
    tweet_texts = []
    for tweet in user_tweets:
        if "text" not in tweet:
            continue
        # filter out retweets
        if tweet["text"].startswith("RT"):
            continue
        if "retweeted_status" in tweet:
            continue
        tweet_texts.append(tweet["text"])
    # (1.1. Ensure the length of the tweet texts list is longer than 10 tweets – otherwise, treat it as statistically unreliable data, and return immediately)
    if len(tweet_texts) < 10:
        return

    # 2. Create a list of probability distributions based on each tweet
    probability_distributions = []
    for tweet_text in tweet_texts:
        probability_distributions.append(sentiment_analyzer.analyze_tweet_probability_distribution(tweet_text))

    # 3. Make 10 000 simulations, and calculate the mean ratio of hateful tweets in relation to all tweets
    mean_hatefulness_score = 0
    num_simulations = 500
    for i in range(1,num_simulations):
        number_of_hateful_tweets = 0
        for prob_distribution in probability_distributions:
            # The sum of all probabilities
            prob_sum = 0
            hateful_prob = 0
            for label in prob_distribution:
                prob_sum += prob_distribution[label]
                if label == SentimentClassification.Hateful:
                    hateful_prob = prob_distribution[label]
            # check if the classification is hateful, based on randomly generated numbers within the probability range
            # recall that random.random() returns a random number between 0 and 1
            if prob_sum * random.random() <= hateful_prob:
                ++number_of_hateful_tweets
        # add this to the hatefulness score
        mean_hatefulness_score += number_of_hateful_tweets / len(probability_distributions)
    # make the sum a mean
    mean_hatefulness_score /= num_simulations

    # 4. Get the minimum element in user_ids, along with its index, and add this user if needed
    # first check if length of user ids is less than the maximum number of users
    global user_ids
    if len(user_ids) < setup.NUMBER_OF_USERS:
        user_ids.append((user_id, mean_hatefulness_score))
        return
    # get the min index
    min_index = 0
    min_hatefulness_score = 2
    for index, (some_user_id, some_hatefulness_score) in enumerate(user_ids):
        if some_hatefulness_score < min_hatefulness_score:
            min_index = index
            min_hatefulness_score = some_hatefulness_score
    # check whether this hatefulness score is greater than the current
    if mean_hatefulness_score > min_hatefulness_score:
        # update the user_ids list
        user_ids[min_index] = (user_id, mean_hatefulness_score)
    # DONE



def new_tweet(tweet):
    # only proceed to score the user if this tweet is classified as hateful
    print("new tweet")
    if sentiment_analyzer.analyze_tweet_verdict(tweet["text"]) == SentimentClassification.Hateful:
        score_user(tweet["user"]["id"])




# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
    main()
