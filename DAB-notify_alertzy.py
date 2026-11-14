# Date: 12-11-2026
# Author: jojopi, based on work by peppe8o
# Version 1.2

# This python scripts sends dx notifications to your alertzy app, when DAB+ Transmitters in a given distance and beyond get received by AbracaDABra (https://github.com/KejPi/AbracaDABra).
# It is based on a tutorial by peppe8o: https://peppe8o.com/smartphone-notifications-raspberry-pi-alertzy/

# you need to set variables in the "variables to be set by user" section before you can run this script the first time
# usage: $ tail -f <pathtoDABscannerfile.csv> | python3 DAB_DX-alertzy.py


import sys
import time
import datetime
import requests
import select

# variables to be set by user
account='<account ID given by alertzy>'
dxdistance = 200.0 #must be float type, minimum distance in km to send notification
receivername = "<name your receiver>"
groupname = "DAB+ DX"
dead_time = 3600 #time in seconds to trigger a notification about same transmitter location again
maxretry = 4 #number of retries to send a message if there is an network error befor it gets dropped
location_whitelist = {} #whitelist, independent of distance

# system variables
location_last_action = {}
system_last_action = 0
retry = 0

# Function to send notifications
def notify(title, message, group):
	global account
	global maxretry
	global retry
	
	files = {
		'accountKey': (None, account),
		'title': (None, title),
		'message': (None, msg),
		'group': (None, group),
	}
	try:
		response = requests.post('https://alertzy.app/send', files=files)
	except requests.exceptions.ConnectionError as err:
		print(datetime.datetime.now())
		print(f"Connection failed: {err}")
		if retry < maxretry:
			print(f"Waiting 60 seconds to try again")
			retry = retry + 1
			time.sleep(60)
			notify(title, message, group)
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
				msg = ("DAB-Notifier is up and running. The last reception report is from "+lt+" local time. The next system report will be send in 12 hours.")
				notify(receivername,msg,"DAB-Notifier reports")
				system_last_action = current_time

	
			# send message if transmitter is in whitelist
			if location in location_whitelist:
				current_time = time.time()
				if location in location_last_action and current_time - location_last_action[location] < dead_time:
					time.sleep(1)
				else:
					distancestr = str(distance)
					msg = ("Received transmitter "+location+": "+distancestr+"km, "+direction+"deg, "+power+"kw, "+levelstr+"dBm, at "+lt+" local time.")
					notify(receivername,msg,groupname)
					location_last_action[location] = current_time
	
			# send message if distance to transmitter is greater than dxdistance set by user in the variable section
			if distance > dxdistance:
				current_time = time.time()
				if location in location_last_action and current_time - location_last_action[location] < dead_time:
					time.sleep(1)
				else:	
					distancestr = str(distance)
					msg = ("Received transmitter "+location+": "+distancestr+"km, "+direction+"deg, "+power+"kw, "+levelstr+"dBm, at "+lt+" local time.")
					notify(receivername,msg,groupname)
					location_last_action[location] = current_time

	else:
		msg = ("There has been no output from AbracaDABra in the last 10 minutes. DAB-Notifier is exiting.")
		notify(receivername,msg,"DAB-Notifier reports")
		print(msg)
		exit()

	time.sleep(1)
