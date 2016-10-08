#!/usr/bin/env python3

# This file provides exactly one method: send_error_message
# If the setup.ERROR_MESSAGE_RECIPIENT_SCREEN_NAME is not set to None,
# an error message should be sent to the recipient via DM

# import twythonaccess for sending DMs
import twythonaccess
# import setup
import setup


# The main function
def send_error_message(message, place):
    dm_name = setup.ERROR_MESSAGE_RECIPIENT_SCREEN_NAME
    if dm_name == None:
        return
    text = "Error in " + place + ": " + str(message)
    if len(text) < 10000:
        twythonaccess.authorize(twitter_app = twythonaccess.TwitterApp.error_messenger).send_direct_message(screen_name = dm_name, text = text)