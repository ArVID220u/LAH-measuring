# this is a file meant to coordinate the database of abusive and nonabusive tweets
# it also acts as a tool to easily classify streamed tweets, via the add_tweet method


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
        save_tweet(tweet, "hateful")
        print("hateful")
    elif ans == "d":
        save_tweet(tweet, "kind")
        print("kind")
    elif ans == "s":
        save_tweet(tweet, "neutral")
        print("neutral")



# save the tweet's text and its id to the corresponding file
def save_tweet(tweet, version):
    filename = version + "_tweets.txt"
    tweetstring = tweet["text"] + "%LOVEAGAINSTHATE||SPLIT%" + str(tweet["id"]) + "%LOVEAGAINSTHATE||SPLIT%"
    with open(filename, "a") as datafile:
        datafile.write(tweetstring)
