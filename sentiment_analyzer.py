# import all nltk stuff for classification
import nltk
# import the sentiment_database for the training
import sentiment_database

# this class has one important method: analyze_tweet, which either returns -1, 0 or 1, each representing different sentiments
# -1 = hatefulness, 0 = neutrality, 1 = kindness
# upon being initialized, it automatically trains the Naive Bayes Classifier, from the nltk library
class SentimentAnalyzer():



    # init!
    # that is: create the classifier, and train it with the data in hateful_tweets.txt and kind_tweets.txt
    def __init__(self):

        # first create three lists: one hateful tweet list and one kind/positive tweet list, and finally one neutral list
        # the tweets in them are completely unprocessed
        hateful_tweets = sentiment_database.get_tweets("hateful")
        kind_tweets = sentiment_database.get_tweets("kind")
        neutral_tweets = sentiment_database.get_tweets("neutral")

        # now we have three lists of tweets
        # transform them into one, so that each element is a tuple consisting of the tweet text, and the sentiment
        all_tweets = []
        for hateful_tweet in hateful_tweets:
            all_tweets.append((hateful_tweet, "hateful"))
        for kind_tweet in kind_tweets:
            all_tweets.append((kind_tweet, "kind"))
        for neutral_tweet in neutral_tweets:
            all_tweets.append((neutral_tweet, "neutral"))

        # now process all the tweet texts
        # the result should be an array, preprocessed_tweets,
        # where each element constitutes a tuple containg (0) an array of selected words, and (1) the sentiment
        preprocessed_tweets = []
        for (tweet, sentiment) in all_tweets:
            preprocessed_tweets.append((self.preprocess(tweet), sentiment))

        # now create the train set
        # the features dictionary is created by applying the make_features function on each preprocessed tweet
        train_set = nltk.classify.apply_features(self.make_features, preprocessed_tweets)

        # do the training!
        self.classifier = nltk.classify.NaiveBayesClassifier.train(train_set)

        # now we have our naive bayes classifier, to be referenced in self.classifier
        # everything's set up!
        
        print("Initialization of SentimentAnalyzer done. Naive Bayes Classifier trained.")

        return



    # preprocess a tweet string by removing mentions, and converting it to a list with selected words
    def preprocess(self, tweet):
        # first remove all mentions at the beginning
        processed_text = self.remove_mentions(tweet)
        # make everything lowercase
        # hmm, note: is this really the behavior we want? maybe abusers more frequently use capitals
        # hmm, note: well, definitely test the accuracy with and without this one
        processed_text = processed_text.lower()
        # whenever the word "not" is found, replace the space after it with a "QQQ"
        # this helps putting the "not" into context, and hopefully properly identifying negated meanings
        processed_text = processed_text.replace("not ", "notQQQ")
        # then, make the processed text a list of words, by utilizing the nltk library
        words = nltk.word_tokenize(processed_text)
        # return this list
        return words



    # remove mentions at the beginning of the string
    def remove_mentions(self, text):
        # strip the tweet text of all @usernames
        no_mentions_text = text
        while no_mentions_text.startswith("@"):
            # remove the first word, which in this case in an @username
            no_mentions_text = no_mentions_text.split(" ", 1)[1]
        return no_mentions_text


    
    # make a proper features dictionary out of a given list of words
    def make_features(self, words):
        # simply set all words to true
        # here, more complex analyzation could be done, if needed
        return dict([(word, True) for word in words])



    # returns an int belonging to {-1, 0, 1} indicating whether the string provided is classified as hateful, neutral or kind
    # this is the most important function
    def analyze_tweet(self, tweet):
        # ok, so simply create the features object
        features = self.make_features(self.preprocess(tweet))
        # classify these features
        # use prob_classify to determine whether to return the best match, or return "neutral" (if low match)
        prob_object = self.classifier.prob_classify(features)
        # the best match
        best_match = prob_object.max()
        # best match probability
        best_match_prob = prob_object.prob(best_match)
        # have a 20 % threshold in place
        if best_match_prob < 0.2:
            print("classification failed – returning neutral value")
            return 0
        if best_match == "hateful":
            print("classified as hateful")
            return -1
        else if best_match == "neutral":
            print("classified as neutral")
            return 0
        else if best_match == "kind":
            print("classified as kind")
            return 1
        else:
            print("serious error in analyze_tweet() in sentiment_analyzer.py. should never, ever happen")
            return 0
