# analyze.py
# compute kwh from well log

import os, sys, time, datetime
DAYS = 7
HOURS = 12
JOULES_PER_KWH = 3.6e6
SCP = True # turn this false if you're running locally on the same device that makes the logs


if(SCP):
	print("Downloading log...")
	os.system("scp wellpump.local:well_*.log . >/dev/null")

# Find the most recent log file and parse it
t = []
for f in os.listdir("."):
	if(len(f)==19):
		t.append(int(f[5:15]))
if(len(t)==0):
	print("No log files found")
	sys.exit()

fn = "well_%d.log" % (max(t))
log = []
for line in open(fn, "r").read().split("\n"):
	log.append(line.split(' '))
print("%d items in %s"%  (len(log), fn))

joules_sum_days = [0]*DAYS
joules_sum_hours = [0]*HOURS
pump_on_ms_days = [0]*DAYS
pump_on_ms_hours = [0]*HOURS
day_timestamp_ms = [0]*DAYS
hour_timestamp_ms = [0]*HOURS

# Get timestamps of last N days, including today (0)
for day in range(DAYS):
	now = datetime.datetime.now()
	midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
	adjusted_midnight = midnight - datetime.timedelta(days=day)
	day_timestamp_ms[day] = time.mktime(adjusted_midnight.timetuple())*1000

# Get timestamps of last N hours
for hour in range(HOURS):
	now = datetime.datetime.now()
	top_of_hour = now.replace(minute=0, second=0, microsecond=0)
	adjusted_top_of_hour = top_of_hour - datetime.timedelta(hours=hour)
	hour_timestamp_ms[hour] = time.mktime(adjusted_top_of_hour.timetuple())*1000

# Compute the joules and pump on time per timeslice
for idx,f in enumerate(log[:-2]):
	t = int(f[0])
	watts = int(f[1])
	ms_length = int(log[idx+1][0])  - t
	joules = watts * (ms_length/1000.0)

	for day in range(DAYS):
		if((day == 0 and t>day_timestamp_ms[0]) or (day!=0 and t>day_timestamp_ms[day] and t<day_timestamp_ms[day-1])):
			joules_sum_days[day] += joules
			if watts>0: pump_on_ms_days[day] += ms_length

	for hour in range(HOURS):
		if((hour == 0 and t>hour_timestamp_ms[0]) or (hour!=0 and t>hour_timestamp_ms[hour] and t<hour_timestamp_ms[hour-1])):
			joules_sum_hours[hour] += joules
			if watts>0: pump_on_ms_hours[hour] += ms_length

# Make CSV-like output
print("hours_ago,kwh,pump_on_minutes")
for hour in range(HOURS):
	kwh = joules_sum_hours[hour]/JOULES_PER_KWH
	pump_on_minutes = (pump_on_ms_hours[hour]/1000.0)/60.0
	print("%d,%f,%f" % (hour, kwh,pump_on_minutes))

print("days_ago,kwh,pump_on_minutes")
for day in range(DAYS):
	kwh = joules_sum_days[day]/JOULES_PER_KWH
	pump_on_minutes = (pump_on_ms_days[day]/1000.0)/60.0
	print("%d,%f,%f" % (day, kwh, pump_on_minutes))



