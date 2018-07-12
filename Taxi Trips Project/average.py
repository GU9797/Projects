import Geohash as geohash2
#import geohash2
from mrjob.job import MRJob
from mrjob.step import MRStep
import mrjob.protocol
import csv
import datetime


def process_time(row):
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


class MRGetAverageDuration(MRJob):

    def mapper(self, _, line):
        for row in csv.reader([line]):         
            pickup_lat = row[17]
            pickup_lon = row[18]
            dropoff_lat = row[20]
            dropoff_lon = row[21]
            trip_seconds = row[4]
            
            #Skips header
            if trip_seconds == 'Trip Seconds': 
                final_geohash = None
                trip_seconds = 0
                continue

            #skips rows with empty cells
            if not pickup_lat or not pickup_lon \
              or not dropoff_lat or not dropoff_lon \
              or not trip_seconds: 
                final_geohash = None
                trip_seconds = 0
                continue
            
            time_of_day = process_time(row)
            if not time_of_day: 
                final_geohash = None
                trip_seconds = 0
            
            else: 
                pickup_geohash = geohash2.encode(float(pickup_lat), float(pickup_lon), 7)
                dropoff_geohash = geohash2.encode(float(dropoff_lat), float(dropoff_lon), 7)
                final_geohash = pickup_geohash + "_" + dropoff_geohash + "_" + time_of_day
        
        yield final_geohash, (trip_seconds, 1)

    def combiner(self, final_geohash, trip_seconds):
        if final_geohash:
            s = 0
            freq = 0 
            for seconds, count in trip_seconds:
                if seconds:
                    freq += count
                    s += int(seconds)
            yield final_geohash, (s, freq)

    def reducer(self, final_geohash, trip_seconds):        
        s = 0
        freq = 0
        for seconds, freqs in trip_seconds:
            s += seconds
            freq += freqs

        #No division by 0 if freq == 0
        if freq == 0:  
            freq = 1

        yield final_geohash, s/freq



if __name__ == '__main__':
    MRGetAverageDuration.run()