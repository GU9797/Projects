'''
CMSC 12300 Spring 2018

Taxi Trips Project
Madeline Kim, Maya Roberts, Edwin Gavis, Mike Gu
'''
import geohash2
from mrjob.job import MRJob
from mrjob.step import MRStep
import mrjob.protocol
import csv
import datetime
import collections
'''
Map reduce function to run through csv file to calculate trip time standard deviation
for each final geohash by comparing trip time to averages. Final geohash is calculated
by encoding pickup and dropoff longitude and latitude as well as time of day the trip
occurred. 

Outputs line by line a final geohash as key with standard deviation
as value
'''
def process_time(row):
    '''
    Takes a row of the csv file and outputs time of day using trip start timestamps.
    Morning (5:00 - 11:59), afternoon/evening (12:00 - 21:59), and night (22:00 - 23:59, 00:00-4:59).
    '''
    timestamp = row[2]
    full_datetime = datetime.datetime.strptime(timestamp, "%m/%d/%Y %I:%M:%S %p")
    t = full_datetime.time()

    if t >= datetime.time(5, 0) and t < datetime.time(12, 0):
        time_of_day = "morning"
    elif t > datetime.time(12, 0) and t < datetime.time(22, 0):
        time_of_day = "aft/eve"
    else:
        time_of_day = "night"

    return time_of_day 


class MRGetStandardDeviation(MRJob):

    def mapper_init(self):
        #creating dictionary from averages file
        myfile = open("2016_2017_avg.csv")
        csv_reader = csv.reader(myfile, delimiter='\t')
        self.d = collections.defaultdict(int)
        for row in csv_reader:
            geohash, average = row
            self.d[geohash] = average

    def mapper(self, _, line):
        trip_variance = 0
        for row in csv.reader([line]):
            #storing coordinates        
            pickup_lat = row[17]
            pickup_lon = row[18]
            dropoff_lat = row[20]
            dropoff_lon = row[21]
            trip_seconds = row[4]
            
            if trip_seconds == 'Trip Seconds': #Skips header
                final_geohash = None
                trip_seconds = 0
                continue
            if not pickup_lat or not pickup_lon \
              or not dropoff_lat or not dropoff_lon: #skips rows with empty cells
                final_geohash = None
                trip_seconds = 0
                continue
            
            time_of_day = process_time(row)

            #Computing final geohash and variance
            if time_of_day:
                try:
                    pickup_geohash = geohash2.encode(float(pickup_lat), float(pickup_lon), 7)
                    dropoff_geohash = geohash2.encode(float(dropoff_lat), float(dropoff_lon), 7)
                    final_geohash = pickup_geohash + "_" + dropoff_geohash + "_" + time_of_day
                    trip_variance = abs((float(trip_seconds) - float(self.d[final_geohash]))**2)
                except:
                    final_geohash = None
                    trip_variance = 0
            else: 
                final_geohash = None
                trip_variance = 0

        yield final_geohash, (trip_variance, 1)

    def combiner(self, final_geohash, trip_variance):
        if final_geohash:
            s = 0
            freq = 0 
            for seconds, count in trip_variance:
                if seconds:
                    freq += count
                    s += int(seconds)
            yield final_geohash, (s, freq)

    def reducer(self, final_geohash, trip_variance):        
        s = 0
        freq = 0
        for seconds, freqs in trip_variance:
            s += seconds
            freq += freqs

        if freq == 0: #No division by 0 if all seconds == None 
            freq = 1
        
        yield final_geohash, (s/freq)**.5

if __name__ == '__main__':
    MRGetStandardDeviation.run()