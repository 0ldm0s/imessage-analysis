import sqlite3

import numpy as np
import pylab as pl

import plotly.plotly as py
import plotly.graph_objs as go

# Parameters
# Number of top senders to look at
LEADERBOARD_LENGTH = 25

conn = sqlite3.connect('/Users/abk/Library/Messages/chat_20160815.db')
c 	= conn.cursor()



#c.execute('SELECT account, DATETIME(date +978307200, \'unixepoch\', \'localtime\') AS date, is_from_me FROM message LIMIT 5');
def plot_message_punchcard(cursor):

	# parameters
	NUM_DAILY_BINS 	= 48		# number of bins per day
	
	c = cursor
	
	# Get first and last message times in dataset, in order to normalize bin values later.
	query = 'SELECT MIN(date)+978307200, MAX(date)+978307200 FROM message'
	c.execute( query )
	timeInterval = c.fetchall()
	totalDurationHours = (timeInterval[0][1] - timeInterval[0][0]) / 3600		# duration between first and last messages in dataset, in hours
	
	# Get message times, in seconds elapsed since midnight local time, for specific day of week (day of week 0-6 where Sunday = 0)
	# this is kind of dumb; could do binning in SQL.
	query = '''SELECT strftime('%s',datetime(date+978307200, 'unixepoch', 'localtime' )) - strftime('%s', strftime('%Y-%m-%d', date+978307200, 'unixepoch', 'localtime')) AS message_time FROM message WHERE strftime('%w',DATETIME(date+978307200, 'unixepoch', 'localtime')) = '''
				
	weekdayMessageTimes = [0,1,2,3,4,5,6]	
	weekdayHistograms = weekdayMessageTimes		
	for day in np.arange(7):
		c.execute(query + '\'' + str(day) + '\'' )
		weekdayMessageTimes[day] = c.fetchall()
		weekdayHistograms[day] = np.histogram(weekdayMessageTimes[day],bins=NUM_DAILY_BINS,range=(0,86400))
		weekdayHistograms[day] = weekdayHistograms[day][0]	# np.histogram returns bin locations too, we don't want those
		
		
		# Return histogram bin values as (messages/hour).
		weekdayHistograms[day] = weekdayHistograms[day] * NUM_DAILY_BINS / (totalDurationHours / 7.0)
	
	data = [
		go.Heatmap(
			z=weekdayHistograms,
			y=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
			colorbar = dict(
				thickness=5,
				ypad=0	
			)
		)]
	
	timeTicks = range(0,3600*24+1,10800)		# x-positions of labeled ticks in seconds
	
	layout = go.Layout(
		title='Message rate (messages/hour)',
		width=800,
		height=600,
		xaxis=dict(
			tickvals= [(x* NUM_DAILY_BINS) / (3600*24)  for x in timeTicks],
			ticktext= ['{:02d}:{:02d}'.format(time // 3600,(time // 60) % 60) for time in timeTicks],
			showgrid=True
		)
	)
	fig = go.Figure(data=data,layout=layout)
	
	py.image.save_as(fig, 'plot.png')
	
	# debug
	arr = np.asarray( weekdayHistograms )
	np.savetxt( "message_histograms.csv", arr, delimiter="," )
	#py.iplot(data)
		
	# temp
# 	fig = pl.figure()
# 	ax = fig.add_subplot(111)
# 	
# 	indexes = np.arange(48)
# 	bars1 	= ax.bar( indexes, weekdayMessageHistograms[0] )
# 	
# 	pl.show()

#plot_message_punchcard(c)

		
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

plot_alltime_leaderboard(c)


# SELECT
#     m.rowid as message_id,
#     DATETIME(date +978307200, 'unixepoch', 'localtime') AS date,
#     id AS address,
#     text
# FROM message AS m
# LEFT JOIN handle AS h ON h.rowid = m.handle_id
# 
# ORDER BY date DESC