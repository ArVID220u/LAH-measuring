#!/usr/bin/env python3


# this simple helper class organizes classifications and makes them more type safe (although python never will be fully type safe)
class SentimentClassification():
    Hateful = "hateful"
    Neutral = "neutral"
    Kind = "kind"
    # a set of all classifications
    classification_set = {"hateful", "neutral", "kind"}
    # a list of all classifications
    classification_list = ["hateful", "neutral", "kind"]
