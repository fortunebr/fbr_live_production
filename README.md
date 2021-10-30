# Live Production

Production live updates to discord and google webhooks. 

</br>

> Note: This project cannot be used directly, as it is build accordingly with a private SQL Server and it's sole purpose is just to notify production updates through webhooks.

</br>

Important notes about program:
--------------------------------
* Program looks for configurations files in root folder "C:/fbr_prodcution/".
* All exceptions are logged in `log.txt` file.
* **SQL Server, Webhook** configuration has to set on `config.ini` file (*a template is provided with repo*).
* Program can be ran at any time, sends hourly production report if and only if the current hour production is greater than 100 pairs
whereas day summary report sends if achieved production is grater than 100 and hour is 8.
* Day summary report not included with Google webhook currently.
* Total number of queries per execution is 3.
* Hourly report is logged to a `pickle` file in the root folder, deleting the file will loose track of previous hourly productions.

</br>

</br>


:blue_heart: from **Fortune Branch**