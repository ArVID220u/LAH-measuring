#!/usr/bin/env python3

# Tweet at the users found in the user id text file (specified in setup.py)
# Not to be run simultaneously as the find_users.py script

# Also have a streamer that replies to replies

# OK, so what's the plan?
# I want to send people tweets at times when they tend to send their offensive tweets.
# This is to magnify the impact of the kind tweet.
# We really don't want the bot getting suspended for sending unsolicited tweets to people.
# Therefore, this procedure needs to be thoroughly scrutinized before launching the actual project.

# This is perhaps not very important. The timing, I mean.
# Rather, I should focus on getting the measurement correct, while still ensuring that each person gets sent one tweet a week.
# Thus, have a week-long loop. At start, it randomly scrambles the user id list, and at a set interval tweets to the users in the list's order.
# This will make the sending of the tweets truly random, and perfectly spread out (so as to minimize the risk of violating the API restrictions).


# import twythonaccess to be able to send tweets
import twythonaccess
from twythonaccess import TwitterApp
# import setup
import setup
# import the streamer
from streamer import TweetStreamer
# import threading
from threading import Thread



# The main function, which should start both the mentions streamer and the tweet loop
def main():
    print("main")



# Set up the mentions streamer, viz. the streamer that should find all tweets mentioning the bot, and reply to them with emoji hearts
# Runs indefinitely, and thus needs error handling
def mentions_streamer():
    print("mentions streamer")


# The tweet loop runs indefinitely, sending one tweet per week per user, at a randomly assigned time.
# Needs thorough error handling.
def tweet_loop():
    print("tweet loop")


# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
    main()
