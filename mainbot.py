# import the twython module
from . import twythonaccess
# import time and sys
import time
# import Thread to be able to run concurrently
from threading import Thread
# randint for the tweet interval
from random import randint
from . import setup


# the main function will be called when this script is called in terminal
# the bash command "python3 mainbot.py" will call this function
def main():
    # declare the global organizer
    global organizer
    organizer = Organizer()
    # create four threads: the both streamers and the both tweet handling loops in relayer
    process_tweets_thread = Thread(target = organizer.process_tweets)
    dayupdater_thread = Thread(target = organizer.dayupdater)
    miner_thread = Thread(target = run_miner)
    # start the four loops simultaneously
    process_tweets_thread.start()
    dayupdater_thread.start()
    miner_thread.start()


# this function will create the miner, and start its filtering
def run_miner():
    # initialize the miner with the api keys from the setup
    miner = Miner(setup.MAIN_CONSUMER_KEY, setup.MAIN_CONSUMER_SECRET, setup.MAIN_ACCESS_TOKEN, setup.MAIN_ACCESS_TOKEN_SECRET)
    # pass the organizer instance to the miner
    miner.organizer = organizer
    # start the filtering
    # ADD ERROR HANDLING HERE
    print("starting miner")
    # add the follow argument with all the user ids from the user id file
    streamer.user.filter(track="i,och,att,det,som,en,på,är,av,för", language="sv")


# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
        main()
