#!/usr/bin/env python3


# this simple helper class organizes classifications and makes them more type safe (although python never will be fully type safe)
class SentimentClassification():
    hate_speech = "hate_speech"
    offensive_but_not_hate_speech = "offensive_but_not_hate_speech"
    not_offensive = "not_offensive"
    # a set of all classifications
    classification_set = {"hate_speech", "offensive_but_not_hate_speech", "not_offensive"}
    # a list of all classifications
    classification_list = ["hate_speech", "offensive_but_not_hate_speech", "not_offensive"]
