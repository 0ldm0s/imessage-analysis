import sqlite3

import numpy as np
import pylab as pl

# Parameters
# Number of top senders to look at
LEADERBOARD_LENGTH = 25

conn = sqlite3.connect('/Users/abk/Library/Messages/chat_20160815.db')
c 	= conn.cursor()



#c.execute('SELECT account, DATETIME(date +978307200, \'unixepoch\', \'localtime\') AS date, is_from_me FROM message LIMIT 5');
def plot_message_punchcard(cursor):
	c = cursor
	
	# Get message times, in seconds elapsed since midnight local time, for specific day of week (day of week 0-6 where Sunday = 0)
	# this is kind of dumb; could do binning in SQL.
	query = '''SELECT 
	strftime('%s',datetime(date+978307200, 'unixepoch', 'localtime' )) - strftime('%s', strftime('%Y-%m-%d', date+978307200, 'unixepoch', 'localtime')) AS message_time
FROM message
WHERE strftime('%w',DATETIME(date+978307200, 'unixepoch', 'localtime')) = '3'
'''
				
	weekdayMessageTimes = [0,1,2,3,4,5,6]	
	weekdayHistograms = weekdayMessageTimes		
	for day in np.arange(7):
		c.execute(query)
		weekdayMessageTimes[day] = np.array(c.fetchall())
		weekdayMessageHistograms = np.histogram(weekdayMessageTimes[day],bins=48,range=(0,86400))
		
	# temp
	fig = pl.figure()
	ax = fig.add_subplot(111)
	
	indexes = np.arange(48)
	bars1 	= ax.bar( indexes, weekdayMessageHistograms[0] )
	
	pl.show()

plot_message_punchcard(c)
		
def plot_alltime_leaderboard(cursor):
	c = cursor
	
	query = '''SELECT
		id,
		COUNT(*) as `num`
	FROM message as m
	LEFT JOIN handle AS h ON m.handle_id = h.ROWID
	GROUP BY handle_id
	ORDER BY num DESC'''
	c.execute(query)

	result = c.fetchall()
	values = [item[1] for item in result]
	names = [item[0] for item in result]

	#Create figure
	fig = pl.figure()
	ax = fig.add_subplot(111)

	indexes = np.arange(LEADERBOARD_LENGTH)
	width = 0.8

	bars1 	= ax.barh( indexes, values[0:LEADERBOARD_LENGTH], width,
						color = 'blue', linewidth=0)

	# Formatting axes and labels
	ax.set_ylim(-width, len(indexes)+width)
	yTickMarks = names[0:LEADERBOARD_LENGTH]
	ax.set_yticks(indexes+width)
	ytickNames = ax.set_yticklabels(yTickMarks)
	pl.setp(ytickNames, rotation=0, fontsize=10)

	ax.set_xlabel('Total messages')
	ax.set_title('Number of messages sent and received by sender')
					
	pl.show()

# SELECT
#     m.rowid as message_id,
#     DATETIME(date +978307200, 'unixepoch', 'localtime') AS date,
#     id AS address,
#     text
# FROM message AS m
# LEFT JOIN handle AS h ON h.rowid = m.handle_id
# 
# ORDER BY date DESC