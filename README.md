# ChatBreakdown

Video demo: https://youtu.be/22ipGKR-pKo    (Website is no longer up due to server costs)

The main code for the backend of the project is shown here.

How it works:

app_static uses tmi.js to collect the chat messages and their associated data, as well as user bans and timeouts.
py_viewer_count.py collects Title and Category information via the API and starts the data proceessing when a channel goes offline.
The data processing is started by py_main_processing.py which executes the main function GetWebData in a new thread.
functions.py stores all the functions used for processing. The results are uploaded to an S3 bucket that is then accessed by the server. Chart.js is used to display the charts.
