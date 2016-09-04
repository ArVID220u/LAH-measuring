# Copy this file to a file named "setup.py", and fill in all desired values

# The username of the bot, on Twitter
# Do not include an @ sign
# Same capitalization as on Twitter is important
TWITTER_USERNAME = "screen name"



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

# The Twitter API keys needed to send tweets
# Only read access is needed
CONSUMER_KEY = "enter your consumer key here"
CONSUMER_SECRET = "enter your secret consumer key here"
ACCESS_TOKEN = "enter your access token here"
ACCESS_TOKEN_SECRET = "enter your secret access token here"
