# ChatBreakdown
The main code for the backend of the project is shown here.

app_static uses tmi.js to collects chat messages and their associated data, as well as user bans and timeouts.
py_viewer_count.py collects Title and Category information via the API and, in a new threadm, starts the data proceessing via py_main_processing.py by calling GetWebData.
functions.py stores all the processing functions and saves the results in the S3 bucket used for the server.
