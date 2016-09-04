# Copy this file to a file named "setup.py", and fill in all desired values

# The username of the bot, on Twitter
# Do not include an @ sign
# Same capitalization as on Twitter is important
TWITTER_USERNAME = "screen name"



# FINDING USERS

# The number of users to find. For a single tweeting bot, something like 1000 users is suitable.
NUMBER_OF_USERS = 1000


# TWEETING

# The tweet with which to always reply to users who mention the bot
REPLY_TWEET = "❤️❤️❤️"

# The path to a file containing a list of responses
# The file should be an ordinary text file, and the responses should be separated by newlines
RESPONSES_PATH = "responses.txt"

# The suffix to add to all responses (except the reply tweet)
RESPONSE_SUFFIX = " ❤️"



# MEASURING

# The path to the file containing the json objects of the collected tweets
# The raw data, essentially
RAW_DATA_PATH = "raw_data.json"
# The path to the csv file containing the score, etc.
PROCESSED_DATA_PATH = "processed_data.csv"

# The path to the file containing the user ids of the accounts to be analyzed
USER_IDS_PATH = "user_ids.txt"



# API KEYS

# Keys for the Tweeting bot. Needs read and write privileges.
TWEETING_CONSUMER_KEY = "enter your consumer key here"
TWEETING_CONSUMER_SECRET = "enter your secret consumer key here"
TWEETING_ACCESS_TOKEN = "enter your access token here"
TWEETING_ACCESS_TOKEN_SECRET = "enter your secret access token here"

# Keys for the Mentions bot. Needs read and write privileges.
MENTIONS_CONSUMER_KEY = "enter your consumer key here"
MENTIONS_CONSUMER_SECRET = "enter your secret consumer key here"
MENTIONS_ACCESS_TOKEN = "enter your access token here"
MENTIONS_ACCESS_TOKEN_SECRET = "enter your secret access token here"

# Keys for the Tweeting bot. Needs read privileges.
MEASURING_CONSUMER_KEY = "enter your consumer key here"
MEASURING_CONSUMER_SECRET = "enter your secret consumer key here"
MEASURING_ACCESS_TOKEN = "enter your access token here"
MEASURING_ACCESS_TOKEN_SECRET = "enter your secret access token here"

# A string indicating the screen name of a twitter user who should receive error messages via DM (again, screen name without '@')
# Set this to None to not send error messages to anyone, and then don't bother filling in the api keys
# Note that the recipient must either follow the bot, or have opened their DMs to all
ERROR_MESSAGE_RECIPIENT_SCREEN_NAME = None
# The error message app needs read, write and DM privileges.
ERROR_MESSAGE_CONSUMER_KEY = "if enabling error messaging, enter your error message twitter application consumer key"
ERROR_MESSAGE_CONSUMER_SECRET = "if enabling error messaging, enter your error message twitter application consumer secret key"
ERROR_MESSAGE_ACCESS_TOKEN = "if enabling error messaging, enter your error message twitter application access token"
ERROR_MESSAGE_ACCESS_TOKEN_SECRET = "if enabling error messaging, enter your error message twitter application secret access token"
