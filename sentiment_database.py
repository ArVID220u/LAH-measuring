# this is a file meant to coordinate the database of abusive and nonabusive tweets
# it also acts as a tool to easily classify streamed tweets, via the add_tweet method

# import sentiment classification
from sentiment_classification import SentimentClassification
# import setup
import setup
# we need to parse the json
import json


# get tweets
# this function returns only the tweets (not the ids)
# accepted arguments: "hateful", "neutral" and "kind"
def get_tweets(version):
    filename = version + "_tweets.txt"
    with open(filename, "r") as datafile:
        # the string %LOVEAGAINSTHATE||SPLIT% is inserted between each tweet in the file
        raw_values = datafile.read().split("%LOVEAGAINSTHATE||SPLIT%")
        # the last object will be empty, since each tweet record is on the form tweet-text%BOTYOURBACK||SPLIT%tweet-id%BOTYOURBACK||SPLIT%
        raw_values.pop()
        # only the items at even indices should be returned, since the others are the tweet ids
        # pass the step parameter to the slicing (step=2)
        return raw_values[::2]




# This function returns a list of the tweets from the hate speech source
# It returns them in the format of a 3-tuple: (tweet text, sentiment classification, confidence level (double between 0 and 1))
def get_hate_tweets():
    # first, load the file (which is in json format) into a list of dictionaries
    # then, extract the relevant data
    # also, if there is anything funky with the text formatting or text encoding, fix that
    raw_data_list = []
    with open(setup.CLASSIFIED_CORPUS_PATH, "r") as data_file:
        raw_data_list = json.loads(data_file.read())
    # now, extract the relevant data
    relevant_data_list = []
    for tweet_dict in raw_data_list:
        # construct the 3-tuple out of the three pertinent values we need
        # the text
        raw_tweet_text = tweet_dict["fields"]["tweet_text"]
        # the text may need processing. I don't know if special characters are presented properly (like emojis – they are important)
        # for now, though, just copy the raw_tweet_text directly
        tweet_text = raw_tweet_text
        # the classification
        # it will be one of the three sentences:
        # 1) "The tweet is not offensive", 2) "The tweet uses offensive language but not hate speech", and 3) "The tweet contains hate speech"
        raw_classification = tweet_dict["fields"]["does_this_tweet_contain_hate_speech"]
        # convert the classification into a sentiment classification
        sentiment_classification = None
        if raw_classification == "The tweet is not offensive":
            sentiment_classification = SentimentClassification.not_offensive
        elif raw_classification == "The tweet uses offensive language but not hate speech":
            sentiment_classification = SentimentClassification.offensive_but_not_hate_speech
        elif raw_classification == "The tweet contains hate speech":
            sentiment_classification = SentimentClassification.hate_speech
        else:
            # uh oh, something's wrong
            raise Exception("Unrecognized classification when reading from the json hate speech file: " + raw_classification)
        # the confidence level – a double in the range [0,1]
        confidence_level = tweet_dict["fields"]["does_this_tweet_contain_hate_speech_confidence"]
        # construct the tuple, and add it to the relevant data list
        relevant_data_list.append((tweet_text, sentiment_classification, confidence_level))
    # return the relevant data list
    return relevant_data_list






# add tweets
# this function gets a tweet dictionary, and asks the comand line interface whether
# the tweet should be added to the abusive list or the nonabusive list
def add_tweet(tweet):
    # print text, and prompt user to evaluate whether hateful, kind or neutral
    print("@" + tweet["user"]["screen_name"] + ": " + tweet["text"])
    ans = input()
    while ans != "a" and ans != "s" and ans != "d" and ans != "h":
        print("type 'a' if the tweet is hateful, 'd' if the tweet is kind, and 's' if neutral. if the tweet is impossible to categorize, skip it with 'h'")
        ans = input()
    if ans == "a":
        # save the tweet to the abusive file
        save_tweet(tweet, SentimentClassification.Hateful)
        print(SentimentClassification.Hateful)
    elif ans == "d":
        save_tweet(tweet, SentimentClassification.Kind)
        print(SentimentClassification.Kind)
    elif ans == "s":
        save_tweet(tweet, SentimentClassification.Neutral)
        print(SentimentClassification.Neutral)



# save the tweet's text and its id to the corresponding file
def save_tweet(tweet, version):
    filename = version + "_tweets.txt"
    tweetstring = tweet["text"] + "%LOVEAGAINSTHATE||SPLIT%" + str(tweet["id"]) + "%LOVEAGAINSTHATE||SPLIT%"
    with open(filename, "a") as datafile:
        datafile.write(tweetstring)
