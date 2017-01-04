#!/usr/bin/env python3

# the manager should be simple
# it is quite specific, and will need heavy customization for the "real" incarnation
# its behavior depends heavily on whether or not this bot is for the treatment or control group


# import setup
import setup
# import tweet.py and measure.py
import tweet
import measure
# we need threading, as always
from threading import Thread
# import datetime
from datetime import datetime
from datetime import time
from datetime import timedelta
# errors, and status updates
import error_messenger
# sleep is critical
from time import sleep




# Main entry point
def main():
    # Start the measuring at the next hour change
    # This is to make the two bots start at the same time (the reference and control group)
    # Which really is necessary, since we want their respective data to be comparable
    # Be sure, though, to not start the two bots at 7.59 and 8.01, since that would make them offset each other by one hour (undersirable outcome)
    # That seems to be quite unlikely, though (assuming the delay in starting time is around 3 minutes, there is only a 5 % risk of the undesirable outcome outlined above)

    # We will have two threads
    tweet_thread = Thread(target = tweet.main)
    measure_thread = Thread(target = measure.main)

    # Calculate the start time
    # 30 days later, we have the tweet start time
    # Another 30 days later, we have the tweet end time
    # And, finally, another 30 days, and we have the (global) end time
    now_time = datetime.utcnow()
    start_time = datetime.combine(now_time.date(), time((now_time.hour + 1) % 24, 0))
    tweet_start_time = start_time + timedelta(days = 30)
    tweet_end_time = tweet_start_time + timedelta(days = 30)
    end_time = tweet_end_time + timedelta(days = 30)

    print("INFORMATION")
    print("Will start at " + str(start_time) + " (UTC).")
    print("Will end at " + str(end_time) + " (UTC).")
    error_messenger.send_error_message("Will start at " + str(start_time) + " (UTC).", "manager.py")
    error_messenger.send_error_message("Will end at " + str(end_time) + " (UTC).", "manager.py")

    # sleep until the start time
    sleep((start_time - datetime.utcnow()).total_seconds())

    # start the measure thread
    measure_thread.start()

    # if we are not in control group, start and manage the tweet thread
    if not setup.IS_CONTROL_GROUP:
        # sleep until tweet start time
        sleep((tweet_start_time - datetime.utcnow()).total_seconds())

        tweet_thread.start()

        # sleep until tweet end time
        sleep((tweet_end_time - datetime.utcnow()).total_seconds())

        # send self destruct message to tweet thread
        tweet.self_destruct()

    # sleep until global end time
    sleep((end_time - datetime.utcnow()).total_seconds())

    # send self destruct message to measure process
    measure.self_destruct()

    # wow, now we're finished
    # send a finished message, and also make it clear that one benefits from waiting one full day before shutting down the program
    print("FINISHED")
    print("Please wait for at least one day before shutting off this bot.")
    error_messenger.send_error_message("Finished. Please wait one day before shutting down.", "manager.py")
    print("Results can be found in " + setup.RAW_DATA_PATH + " and " + setup.PROCESSED_DATA_PATH + ".")
    print("Goodbye.")





# if called directly (as in "python3 mainbot.py"), then call main() function
if __name__ == "__main__":
    main()
