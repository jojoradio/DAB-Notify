# Date: 17-11-2026
# Author: jojopi, based on work by PD2HASB
# Version 1.1

# This python scripts sends dx notifications to your dapnet pager, when DAB+ Transmitters in a given distance and beyond get received by AbracaDABra (https://github.com/KejPi/AbracaDABra).
# It is based on Python-to-DapNET by PD2HSB: https://github.com/PD2HSB/Python-to-DapNET/tree/main

# you need to set variables in the "variables to be set by user" section before you can run this script the first time
# usage: $ tail -f <pathtoDABscannerfile.csv> | python3 DAB-notify_dapnet.py


import sys
import time
import datetime
import requests
import json
import select

# variables to be set by user
  
callsign = "<hampager.de username>"
password = "<hampager.de password" 
url = "http://www.hampager.de/api/calls" # set hampager API URL
dxdistance = 200.0 #must be float type
tocall = "<recipents callsign>"
groupname = "<txgroup>"#"dl-ni-weserems" #name of valid tx-group, please keep this restrictive to reduce system load.
dead_time = 3600 #time in seconds to trigger a notification about same transmitter location again
maxretry = 4 #number of retries to send a message if there is an network error befor it gets dropped
location_whitelist = {} #whitelist, independent of distance

# system variables
location_last_action = {}
system_last_action = 0
retry = 0

# Function to send dapnet messages
def notify(call,message,txgroup):
	global retry
	global maxretry
	global url
	for cs in call.split(","):
		data = {
			"text": message,
			"callSignNames": [cs],
			"transmitterGroupNames": [txgroup],
			"emergency": False
		}

		#url = "http://www.hampager.de/api/calls"
		headers = {"Content-Type": "application/json"}
		auth = (callsign, password)

		try:
			response = requests.post(url, headers=headers, auth=auth, data=json.dumps(data))
			print(datetime.datetime.now())
			print("Message send to "+cs)
		except requests.exceptions.ConnectionError as err:
			print(datetime.datetime.now())
			print(f"Error sending message: {err}")
			if retry < maxretry:
				print(f"Waiting 60 seconds to try again")
				retry = retry + 1
				time.sleep(60)
				notify(call, message, txgroup)
			else:
				print(datetime.datetime.now())
				print(f"Reached maximum number of reconnects, dropping message.")
				retry = 0
				return True
		retry = 0
		return True

# Main program
while True:

	# read output  of scanner csv line by line with input timeout exception after 10 minutes (600 seconds)
	a, b, c = select.select([sys.stdin], [], [], 600)
	if (a):
		line = sys.stdin.readline()
		line = line.rstrip("\n")
		csv = list(line.split(';'))
		# save csv parameters to variables
		lt = csv[0]
		if lt != "Time (CET)":	# skip line if line is header
			location = csv[11]
			power = csv[12]
			direction = csv[14]
			try:
				distance = float(csv[13])
			except ValueError:
				print("Invalid input: cannot convert distance to float")
				distance = 0.0
			# calculate RF level of the transmitter signal from multiplex RF level (csv[7]) and difference of single transmitter signal to RF level (csv[10])
			try:
				level = float(csv[7]) + float(csv[10])
			except ValueError:
				print("Invalid input: cannot convert level to float")
				level = 0.0
			levelstr = str(round(level, 1))

			# send system info message every 12 hours
			current_time = time.time()
			if current_time - system_last_action < 43200:
				time.sleep(1)
			else:
				msg = ("DAB-notifier is up and running.")
				notify(tocall,msg,groupname)
				system_last_action = current_time


			# send message if transmitters is in whitelist
			if location in location_whitelist:
				current_time = time.time()
				if location in location_last_action and current_time - location_last_action[location] < dead_time:
					time.sleep(1)
				else:	
					distancestr = str(distance)
					msg = (location+": "+distancestr+"km, "+direction+"deg, "+power+"kw, "+levelstr+"dBm")
					if len(msg) > 80:
						msg = msg[:76] + "..."
					notify(tocall,msg,groupname)
					location_last_action[location] = current_time

			# send message if distance to transmitter is greater than dxdistance set by use in the variable section
			if distance > dxdistance:
				current_time = time.time()
				if location in location_last_action and current_time - location_last_action[location] < dead_time:
					time.sleep(1)
				else:	
					distancestr = str(distance)
					msg = (location+": "+distancestr+"km, "+direction+"deg, "+power+"kw, "+levelstr+"dBm")
					if len(msg) > 80:
						msg = msg[:76] + "..."
					notify(tocall,msg,groupname)
					location_last_action[location] = current_time

	else:
		msg = ("There has been no output from AbracaDABra in the last 10 minutes. Exiting now.")
		notify(tocall,msg,groupname)
		print(msg)
		exit()

	time.sleep(1)
