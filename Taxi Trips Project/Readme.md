CMSC123 Project: Chicago Taxi Trips

Edwin Gavis, Mike Gu, Maya Jones and Madeline Kim

Code:

	sample.py - random sampling from csv files of trips

	average.py - calculates average durations of trips between two locations by time of day

	std.py - calculates standard deviations for the trip duration averages

	filter.py - filters trips to return only those more than 1 standard deviation away from
	the average duration for their time and locations  

	intersections.py - calculates coordinates of intersections between trips

	job_conf - configuration and boostrapped installation settings for MRJob when run
	on Google Dataproc clusters


sample.py is run locally, while the rest are run on Google Dataproc
clusters via the Yelp MRJob dataproc utility (versions 0.5.1 & 0.6.2).


Other Files:

	2016_2017_<avg/std>.csv - average trip durations and standard
	deviations computed using average.py and std.py 

	taxi-trips-cs123-project-writeup.pdf - our final report
