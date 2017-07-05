
Script for the Insight Data Engineering challenge focusing on implementing a social network based on customers of a company. Goal is to analyze purchases within a social network of users, and detect any behavior that is far from the average within that social network.
 
Although no third-party libraries are required to run this Python script, it does require importing two libraries from Python’s standard libraries (sys and json). The sys is required to handle command line arguments for the files to be processed and to exit the script when things fail.  The json library is required to parse json strings. 

The script tries to provide output of improperly-formatted lines if errors occur.
For now, I’ve avoided parsing the timestamps as datetimes for simplicity (otherwise it could have been done using the datetime module) within the sorting stage. 

Since the script is only one file, it can be run with:
python ./src/transaction_monitor.py ./log_input/batch_log.json ./log_input/stream_log.json ./log_output/flagged_purchases.json


