# to be able to sleep in the loops
from time import sleep
# import datetime so that the current date can be extracted
import datetime
# import twythonaccess, to be able to send tweets
from . import twythonaccess
# import random, so as to be able to choose a random sample of tweets
import random
from . import setup

# the Organizer class will function as a controller, coordinating tasks in an efficient manner
# there will only exist one organizer instance, which is accessed in three threads simultaneously
class Organizer():

    # declare the two lists below as class variables.
    # this means that they will be shared by all instances
    # though, for memory reasons, only having one instance of relayer is preferred

    # the tweets which are to be processed, i.e. they have been collected by the miner
    to_be_processed_tweets = []

    # the current day's total score
    # resetted each day
    dayscore = 0

    # frequency for the offensive, neutral and kind tweets, respectively
    offensive_frequency = 0
    neutral_frequency = 0
    kind_frequency = 0

    # the number of tweets this day
    numberperday = 0

    # array of tweet dictionaries of all tweets processed
    all_tweets = []

    # the count of analyzed tweets per user id
    analyzed_users_count = {}


    # use an initializer so that every instance is forced to be initialized with an analyzer instance
    def __init__(self, analyzer):
        self.analyzer = Analyzer()


    # the add tweet method is called for every tweet from the miner
    # filter out retweets, for example
    # all tweets that aren't filtered out are put in the to_be_processed_tweets list
    def add_tweet(self, tweet):
        # filter out tweets starting with RT
        if tweet["text"].startswith("RT"):
            return
        # the tweet has endured all filtering rules, now add it to the list
        print("new tweet")
        self.to_be_processed_tweets.append(tweet)


    # this process_tweets function runs in its own thread, undisturbed
    # it checks for new tweets, analyzes and scores them, and then tweaks the dayscore among other things
    def process_tweets(self):
        # this loop should be run indefinitely
        while True:
            # if there's currently no tweet in to_be_processed_tweets, wait for one second
            # this will probably never happen. maybe during night time, though
            while len(self.to_be_processed_tweets) == 0:
                sleep(1)
            # copy all tweets from the to_be_processed list to a local list
            # then reset it
            local_to_be_processed = self.to_be_processed_tweets
            self.to_be_processed_tweets = []
            # one of the tweets in local_to_be_processed is to be analyzed and scored
            # determine which (if there are more than one), using the prioritize method
            chosen_tweet = self.prioritize(local_to_be_processed)
            # increment the count in the analyzed_users_count
            # the aim is to get an as balanced as possible subset of the tweets from the test group
            if chosen_tweet["user"]["id"] in self.analyzed_users_count:
                selfanalyzed_user_count[chosen_tweet["user"]["id"]] += 1
            else:
                self.analyzed_user_count[chosen_tweet["user"]["id"]] = 1
            # analyze and score the tweet
            score = self.analyzer.score(chosen_tweet)
            # update today's general score
            self.dayscore += score
            # increment the number per day
            self.numberperday += 1
            # increment the correct frequency
            if score < 0:
                self.offensive_frequency += 1
            elif score > 0:
                self.kind_frequency += 1
            elif score == 0:
                self.neutral_frequency += 1
            # finally add the tweet id, the user id, the timestamp and the score to the all_tweets array
            # do it in dictionary form, for easy conversion to json later
            self.all_tweets.append({"tweet_text": chosen_tweet["text"],
                                    "tweet_id": chosen_tweet["id"],
                                    "user_id": chosen_tweet["user"]["id"],
                                    "timestamp": chosen_tweet["created_at"],
                                    "score": score})
            # now, the loop should continue with next tweet


    # the dayupdater function takes all the class variables and stores them securely in the data files
    # thus, the data files are updated once every day
    # the score and frequency numbers are added in a csv file
    # all the variables should be resetted, as well
    # it runs in its own thread, indefinitely
    def dayupdater(self):
        current_day = datetime.date.day
        while True:
            # check if day has changed
            if datetime.date.day == current_day:
                sleep(30 * 60)
                continue
            current_day = datetime.date.day
            # new day, updated the raw data


    # this function returns one element from a list
    # it prioritizes based on whether the user has already been analyzed and tracked
    def prioritize(self, base_list):
        # iterate over each element in the list
        minelement = None
        mincount = 100000
        for element in base_list:
            if element["user"]["id"] not in self.analyzed_users_count:
                # this means the user id has never been counted, thus it has to be the smallest one
                return element
            if self.analyzed_users_count[element["user"]["id"]] < mincount:
                # update minelement
                minelement = element
                mincount = self.analyzed_users_count[element["user"]["id"]]
        # return the minelement
        return minelement
