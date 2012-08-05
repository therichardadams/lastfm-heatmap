#!/usr/bin/env python
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

print "Starting data analysis."
user = sys.argv[1]
monthname = ["","January","February","March","April","May","June","July","August","September","October","November","December"]

# Open the temp file and determine the years for which we have data, and the highest count for any individual bin
# All the histograms can then have the same extents set to a unified scale
f = open('lastfmplaytimes.tmp')
count = {}
minyear = 3000
maxyear = 0
for line in f:
	year = int(line[0:4])
	month = int(line[5:7])
	day = int(line[11])
	hour = int(line[13:15])
	if ( year > maxyear ):
		maxyear = year
	if ( year < minyear ):
		minyear = year
	if not count.has_key( str(year) + str(month) + str(day) + str(hour) ):
		count[str(year) + str(month) + str(day) + str(hour)] = 1
	else:
		count[str(year) + str(month) + str(day) + str(hour)] += 1
perbox = count.values()
maxcount = np.max(perbox)
years = (maxyear-minyear)+1
f.close()
print "First pass done. Filling histograms."

# Fill the numpy histograms, one for each month of each year
for year in range(minyear, maxyear+1): # This entire loop is hideously inefficient and needs a rewrite to avoid looping
	for month in range(1, 13):
		hour = []
		day = []
		
		f = open('lastfmplaytimes.tmp')
		for line in f:
			if ( int(line[0:4]) == year and int(line[5:7]) == month ):
				day.append( int(line[11]) )
				floathour = float(line[13:15]) + float(line[16:18])/60
				hour.append(floathour)
		f.close()
		
		heatmap, xedges, yedges = np.histogram2d( hour, day, bins=(24,7), normed=False, range=((0,24),(1,8)) )
		extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]

		if len(hour):
			index = (year-minyear)*12+month
			plt.subplot(years,12,index)
			frame = plt.gca()
			frame.xaxis.set_ticks(np.arange(1.5, 8.5))
			frame.xaxis.set_ticklabels(["M","Tu","W","Th","F","Sa","Su"])
			frame.set_xlabel(monthname[month], color='white', size='24', labelpad=12)
			frame.yaxis.set_ticks([0,3,6,9,12,15,18,21,24])
			frame.tick_params(axis='x', colors='white')
			frame.tick_params(axis='y', colors='white')
			plt.imshow(heatmap, extent=extent,cmap=plt.get_cmap("hot"), vmin=0, vmax=maxcount, interpolation='nearest')

print "Done. Adding labels to plots."

def titlepos(figs): # This crazy formula keeps the title in a good place independent of the number of years of data
	return 0.945-0.328*math.exp(-1.24*figs)

def labelpos(fig, figs): # This is close, but not quite right in putting the year labels in the right place
	centrepoint = (figs+1.0)/2
	gap = 0.82/figs
	pos = 0.495 + gap*(fig-centrepoint)
	return pos

# Add the title and year markers
plt.figtext(0.04, titlepos(years), user + ' last.fm Heatmaps', color='w', size='72')
for year in range(minyear, maxyear+1):
	plt.figtext(0.04, labelpos(maxyear+1-year, years), year, color='w', size='48')

# Add the legend bar
fig = plt.gcf()
cax = fig.add_axes([0.935, 0.1, 0.02, 0.8])
cax.tick_params(axis='y', colors='white', labelsize=24)
plt.colorbar(cax=cax)

print "Done. Saving file."
# Save the file out to disk
fig.set_size_inches(30,years*6.5+6) # Expands height to fit appropriate number of years of data
plt.savefig('heatmap.png', facecolor='0.15', edgecolor='none')
# plt.savefig('heatmap.png', facecolor='#4a525a', edgecolor='none') # Blue-grey background
# plt.savefig('heatmap.png', facecolor='0.15', edgecolor='none', dpi=300) # Hi-DPI output
# plt.savefig('heatmap.pdf', facecolor='0.15', edgecolor='none') # PDF Output
print "Done."
