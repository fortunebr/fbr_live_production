# Live Production Monitoring

Production live updates to discord, slack and google webhooks. 

 This project cannot be used directly, as it is build accordingly with a private SQL Server and it's sole purpose is just to notify production updates through web apis. But, yeah.. you are free to use this and develop your own or give me some suggestions. 

 > FYI: I will not take any responsibilities for any consequences whatsoever which may result from using this app or any related actions.

</br>

### Screen shots:
- [Slack message sample](https://i.imgur.com/jrZhli5.jpg)



</br>

### Requirements
* [Microsoft ODBC Driver 17 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=56567) 

### Setup
See the latest version for the application [here](https://github.com/kalaLokia/fbr_production/releases).
1. Extract/install contents in the file `fbr_production.zip`  to "`C:/fbr_production/`".
2. Enter your webhook url/api token in the `config.ini` file. Sample format given below for both [Google](https://developers.google.com/chat/how-tos/webhooks) and [Slack](https://api.slack.com/messaging/webhooks),

    ```
    [WEBHOOK]
    GOOGLE = https://chat.googleapis.com/xxxxxxxxxxxxxxxxxxx
    SLACK = https://hooks.slack.com/services/xxxxxxxxxxxxxxx
    ```
    You can also give SQL Server credentials if it is different from the default or if you don't want to run the program in SQL Server but in another system, add the details in below format:
    ```
    [SQL SERVER]
    SERVER = server name
    DATABASE = database name
    UID = userid
    PWD = password
    ```
3. Run the `production.exe`
    >* **Microsoft ODBC driver 17** is required for the program to run successfully.
    >* If all went well, you can see the latest production report where ever your webhook(s) configured (google | slack).
    >* If something goes wrong, it will be logged in `C:/fbr_production/log.txt`.
#### Setting up for hourly schedule using Windows Task Scheduler
4. Search for **Task Scheduler** in windows search menu, open it.
5. Select Create Task (right top)
6. Tab "General" : 
    * Give a name (suggested: Custom Production Logging)
    * Select "Run whether user is logged on or not"
    * Select "Run with highest privileges"
7. Tab "Triggers":
    * Select "New" (bottom option)
    * Select "Daily"
    * Change Start time minutes and seconds to HH:00:02 (leave the hour (HH) as current hour)
    * **Advanced settings option:**
    * Select "Repeat task every" and set it to **1 hour**
    * Select "Stop all running tasks at end of repetition duration"
    * Select "Stop task if it runs longer than" and set it to *30 minutes* or the lowest
    * Select Enabled (tick) and Press **OK**
8. Tab "Actions":
    * Select "New" (bottom option)
    * Set Action as "Start  a program"
    * Browse and select the Program/Script in path "C:/fbr_production/production.exe".
    * Press **OK**
9. Tab "Conditions":
    * In Networkl options, select "Start only if the following network connection is available" and set it to "Any connection"
10. Press **OK** and enter the user password if it is asked.

~Enjoy


> Note: *Production time set to: 08:00 to 08:00 (next day).*

