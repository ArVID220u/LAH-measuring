# This module provides the api twython object, which is used to access the api

# import time, to enable the sleep function
import time

# Import twython
from twython import Twython

# import the setup containing the api keys
from . import setup




# The api variable is the way to access the api
# there are two authorization possiblities: main or mentions application
def authorize(main=True):
    # Increment number of requests made in main application
    global requests_since_last_sleep
    requests_since_last_sleep += 1
    # authorize
    return Twython(setup.CONSUMER_KEY, setup.CONSUMER_SECRET, setup.ACCESS_TOKEN, setup.ACCESS_TOKEN_SECRET)


# Store number of requests, so that they won't exceed the rate limit
requests_since_last_sleep = 0
# This method is called every time a request is to be made
# If the requests variable is over limit, then it sleeps for 16 minutes
# if the requests variable isn't over limit, then do nothing
def sleep_if_requests_are_maximum(limit):
    global requests_since_last_sleep
    print("Requests since last sleep: " + str(requests_since_last_sleep))
    if requests_since_last_sleep >= limit:
        print("will sleep")
        time.sleep(16*60)
        print("has slept")
        # reset requests
        requests_since_last_sleep = 0
