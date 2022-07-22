# ChatBreakdown
The main code for the backend of the project is shown here.

app_static is the main part of the data collection using tmi.js it collects the chat messages and associated data, bans and timeouts.
py_viewer_count.py collects Title and Category information via the API and starts the data proceessing via py_main_processing.py in a new thread as it calls the GetWebData function.
functions.py stores all the processing functions and saves the results in the S3 bucket used for the server.
