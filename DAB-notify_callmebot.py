# Date: 17-11-2026
# Author: jojopi
# Version 1.2

# you need to set variables in the "variables to be set by user" section before you can run this script the first time
# usage: $ tail -f <pathtoDABscannerfile.csv> | python3 DAB-notify_callmebot.py


import sys
import time
import datetime
import requests
import select
import callmebot

# variables to be set by user

dxdistance = 200.0 #must be float type, minimum distance in km to send notification
dead_time = 3600 #time in seconds to trigger a notification about same transmitter location again
maxretry = 4
location_whitelist = {} #whitelist, independent of distance

# system variables
location_last_action = {}
system_last_action = 0
retry = 0

def notify(message):
	global maxretry
	global retry
	try:
	# uncomment to send telegram message
		callmebot.telegram(message)
	except requests.exceptions.ConnectionError as err:
		print(datetime.datetime.now())
		print(f"Connection failed: {err}")
		if retry < maxretry:
			print(f"Waiting 60 seconds to try again")
			retry = retry + 1
			time.sleep(60)
			notify(message)
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
				msg = ("DAB-notifier is up and running. The last reception report is from "+lt+" local time. The next system report will be send in 12 hours.")
				notify(msg)
				system_last_action = current_time

	
			# send message if transmitter is in whitelist
			if location in location_whitelist:
				current_time = time.time()
				if location in location_last_action and current_time - location_last_action[location] < dead_time:
					time.sleep(1)
				else:
					distancestr = str(distance)
					msg = ("Received transmitter "+location+": "+distancestr+"km, "+direction+"deg, "+power+"kw, "+levelstr+"dBm, at "+lt+" local time.")
					notify(msg)
					location_last_action[location] = current_time
	
			# send message if distance to transmitter is greater than dxdistance set by user in the variable section
			if distance > dxdistance:
				current_time = time.time()
				if location in location_last_action and current_time - location_last_action[location] < dead_time:
					time.sleep(1)
				else:	
					distancestr = str(distance)
					msg = ("Received transmitter "+location+": "+distancestr+"km, "+direction+"deg, "+power+"kw, "+levelstr+"dBm, at "+lt+" local time.")
					notify(msg)
					location_last_action[location] = current_time

	else:
		msg = ("There has been no output from AbracaDABra in the last 10 minutes. DAB-notifier is exiting.")
		notify(msg)
		print(msg)
		exit()

	time.sleep(1)
