# DAB-Notify
Python scripts to notify user about distant transmitters received by AbracaDABra.
DAB-Notify sends notifications to alertzy app or a DAPNET pager (licensed amateur radio operators only). 

# Requirements
An instance of Abracadabra must be running. The Software can be found here: https://github.com/KejPi/AbracaDABra

Following Python-modules need to be installed: requests, json, select\
They can be installed by using pip3:
```
pip3 install requests
pip3 install json
pip3 install select
```
# Setup AbracaDABra before using DAB-Notify
When you have installed and set up AbracaDABra according to manual of AbracaDABra you find in the repository linked above and you can already listen to radio, it is time to open the scanner function. There are only a few things you need to set up:

1. set the file path you want the scanner to store the logs.
<img width="1551" height="902" alt="Bildschirmfoto 2026-11-14 um 16 04 23" src="https://github.com/user-attachments/assets/57f71ee3-8c77-4ed4-a4c0-2843cfdd3820" />

2. set location, so a distance between transmitter and receiver can be calculated. You can input a fix GPS position ore use a GPS receiver. These settings can be found in the Settings/TII menu. Also you need to download the transmitter database in the top of the TII settings page.
<img width="1551" height="902" alt="Bildschirmfoto 2026-11-14 um 16 02 20" src="https://github.com/user-attachments/assets/71d647f2-843f-496f-92bc-a50eeb99d2e9" />



3. set the scanner to automatically save to csv, set decoding modus and the numbers of scans. The number of scans should be Inf (-1):
<img width="1551" height="902" alt="Bildschirmfoto 2026-11-14 um 16 05 37" src="https://github.com/user-attachments/assets/27d4be98-0349-4d55-9828-914f6d631c81" />


Now AbracaDABra is ready and you can hit the start button.

# DAB-Notify for alertzy

## Set up DAB-Notify for alertzy
First download DAB-notify_alertzy.py from this repository, download the alertzy app for iOS or Android and  follow their tutorial on how to set it up: https://alertzy.app
When you got your account ID you can open DAB-notify_alertzy.py with an editor an set it up.
There are only a few variables to be set to your needs:
```
# variables to be set by user
account='<account ID given by alertzy>'
dxdistance = 200.0 #must be float type, minimum distance in km to send notification
receivername = "<name your receiver>"
groupname = "DAB+ DX"
dead_time = 3600 #time in seconds to trigger a notification about same transmitter location again
maxretry = 4 #number of retries to send a message if there is an network error befor it gets dropped
location_whitelist = {} #whitelist, independent of distance
```
You can name the receiver as you like. It might help you to see which receiver sent you a notification if you have more than one running. The dxdistance is the minimum distance in km of a transmitter to your location to trigger a notification. When a given transmitter gets received over and over again, DAB-Notify will not send you a notification again and again. It will wait as many seconds as set in dead_time before sending a notification again.\
Transmitters given in location_whitelist trigger notifications independent from dxdistance. Be sure to input the exact names as given by the transmitter database. You can copy them out of list of the scanner for example.\
It then should look like this:
```
location_whitelist = {"Næstved/Øverup/Køgevej 291","Garz (Rügen)"}
```
## Run DAB-Notify for alertzy
```
$ tail -f <pathtoDABscannerfile.csv> | python3 DAB-notify_alertzy.py
```
You will find the csv file you need when the scanner is active only. Be sure to copy the path to the csv file the scanner is actively writing to. If everything works as expected, you will get a notification that DAB-Notify is running as soon as the first entry is written to the file.\

DAB-Notify for alertzy is based on a tutorial by peppe8o: https://peppe8o.com/smartphone-notifications-raspberry-pi-alertzy/

# DAB-Notify for DAPNET
## Set up DAB-Notify for DAPNET
Make sure to have a amateur radio license, a pager and a DAPNET-account. To create an account and learn more about DAPNET visit https://www.hampager.de/#/

As soon as you have received your account details for DAPNET access you can setup DAB-Notify_dapnet.py
```
callsign = "<hampager.de username>"
password = "<hampager.de password>" 
url = "http://www.hampager.de/api/calls" # set hampager API URL
dxdistance = 200.0 #must be float type
tocall = ""
groupname = "" #name of valid tx-group, please keep this restrictive to reduce system load.
dead_time = 3600 #time in seconds to trigger a notification about same transmitter location again
maxretry = 4 #number of retries to send a message if there is an network error befor it gets dropped
location_whitelist = {} #whitelist, independent of distance
debug = 0
```
Set your callsign and hamper.de password. The default url is valid for access from the internet. Use a different url if you access the DAPNET API through the hamnet. The dxdistance is the minimum distance in km of a transmitter to your location to trigger a notification. Set the callsign you want to sent the pager messages to in tocall. The txgroup must be set in the groupname variable. It must be a valid txgroup or the DAPNET will drop the message. Please make sure to set the geographically correct group so messages will be transmitted in your area. But do not set the region too wide to avoid unnecessary airtime.\
When a given transmitter gets received over and over again, DAB-Notify will not send you a notification again and again. It will wait as many seconds as set in dead_time before sending a notification again.\
Transmitters given in location_whitelist trigger notifications independent from dxdistance. Be sure to input the exact names as given by the transmitter database. You can copy them out of list of the scanner for example.\
It then should look like this:
```
location_whitelist = {"Næstved/Øverup/Køgevej 291","Garz (Rügen)"}
```
If you like to get detailed informations about errors occur when delivering a message to DAPNET set debug = 1

## Run DAB-Notify for dapnet
```
$ tail -f <pathtoDABscannerfile.csv> | python3 DAB-notify_dapnet.py
```
You will find the csv file you need when the scanner is active only. Be sure to copy the path to the csv file the scanner is actively writing to. If everything works as expected, you will get a notification that DAB-Notify is running as soon as the first entry is written to the file.\

DAB-notify_dapnet.py based on Python-to-DapNET by PD2HSB: https://github.com/PD2HSB/Python-to-DapNET/tree/main

# DAB-Notify for CallMeBot

## Set up DAB-Notify for CallMeBot
Install and set up CallMeBot according to https://github.com/jutge-org/callmebot Make shure to set you username right in ./.secrets/secrets.yml \
At the moment DAB-notify_callmebot.py works for direct messages via telegram only.

## Run DAB-Notify for CallMeBot
```
$ tail -f <pathtoDABscannerfile.csv> | python3 DAB-notify_callmebot.py
```
You will find the csv file you need when the scanner is active only. Be sure to copy the path to the csv file the scanner is actively writing to. If everything works as expected, you will get a notification that DAB-Notify is running as soon as the first entry is written to the file.\
