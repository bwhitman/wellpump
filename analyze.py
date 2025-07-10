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

joules_sum_days = {}
joules_sum_hours = {}
midnight_timestamp_ms = [0]*DAYS
hour_timestamp_ms = [0]*HOURS

# Get last N days, including today (0)
for day in range(DAYS):
	now = datetime.datetime.now()
	midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
	adjusted_midnight = midnight - datetime.timedelta(days=day)
	midnight_timestamp_ms[day] = time.mktime(adjusted_midnight.timetuple())*1000
	joules_sum_days[day] = 0

# Get last N hours
for hour in range(HOURS):
	now = datetime.datetime.now()
	top_of_hour = now.replace(minute=0, second=0, microsecond=0)
	adjusted_hour = top_of_hour - datetime.timedelta(hours=hour)
	hour_timestamp_ms[hour] = time.mktime(adjusted_hour.timetuple())*1000
	joules_sum_hours[hour] = 0


for idx,f in enumerate(log[:-2]):
	t = int(f[0])
	watts = int(f[1])
	ms_length = int(log[idx+1][0])  - t
	joules = watts * (ms_length/1000.0)

	for day in range(DAYS):
		if((day == 0 and t>midnight_timestamp_ms[0]) or (day!=0 and t>midnight_timestamp_ms[day] and t<midnight_timestamp_ms[day-1])):
			joules_sum_days[day] = joules_sum_days.get(day, 0) + joules

	for hour in range(HOURS):
		if((hour == 0 and t>hour_timestamp_ms[0]) or (hour!=0 and t>hour_timestamp_ms[hour] and t<hour_timestamp_ms[hour-1])):
			joules_sum_hours[hour] = joules_sum_hours.get(hour, 0) + joules


print("hours_ago,kwh,wh")
for hour in range(HOURS):
	kwh = joules_sum_hours[hour]/JOULES_PER_KWH
	print("%d,%f,%d" % (hour, kwh, kwh*1000.0))

print("days_ago,kwh,wh")
for day in range(DAYS):
	kwh = joules_sum_days[day]/JOULES_PER_KWH
	print("%d,%f,%d" % (day, kwh, kwh*1000.0))



