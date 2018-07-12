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
from mr3px.csvprotocol import CsvProtocol
'''
Map reduce function to run through csv file to filter trips whose trip time is greater
than standard deviation for corresponding final geohash. Final geohash is calculated
by encoding pickup and dropoff longitude and latitude as well as time of day the trip
occurred. 

Outputs a filtered csv file with same format as original
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

class MRFilterTrips(MRJob):

    OUTPUT_PROTOCOL = CsvProtocol

    def mapper_init(self):
        #creating dictionary from averages file
        myfile = open('245_avg.csv')
        csv_reader = csv.reader(myfile, delimiter='\t')
        self.d_avg = collections.defaultdict(int)
        for row in csv_reader:
            geohash, average = row
            self.d_avg[geohash] = average

    def mapper(self, _, line):
        trip_difference = 0
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
            
            #Computing final geohash and difference from trip time to the average
            time_of_day = process_time(row)
            try:
                pickup_geohash = geohash2.encode(float(pickup_lat), float(pickup_lon), 7)
                dropoff_geohash = geohash2.encode(float(dropoff_lat), float(dropoff_lon), 7)
                final_geohash = pickup_geohash + "_" + dropoff_geohash + "_" + time_of_day
                trip_difference = abs((float(trip_seconds) - float(self.d_avg[final_geohash])))
            except:
                final_geohash = None
                trip_seconds = 0

        yield row, (final_geohash, trip_difference)

    def combiner_init(self):
        #creating dictionary from standard deviations file
        myfile2 = open('245_std.csv')
        csv_reader2 = csv.reader(myfile2, delimiter='\t')
        self.d_std = collections.defaultdict(int)
        for row in csv_reader2:
            geohash, std = row
            self.d_std[geohash] = std

    def combiner(self, row, trip_data):
        #checks to see if trip time is greater than or equal to standard deviation
        for geohash, trip_difference in trip_data:
            if geohash != None:
                if trip_difference >= float(self.d_std[geohash]):
                    yield row, (geohash, trip_difference)

    def reducer_init(self):
        #creating dictionary from standard deviations file
        myfile3 = open('245_std.csv')
        csv_reader3 = csv.reader(myfile3, delimiter='\t')
        self.d_std2 = collections.defaultdict(int)
        for row in csv_reader3:
            geohash, std = row
            self.d_std2[geohash] = std

    def reducer(self, row, trip_data):   
        #checks to see if trip time is greater than or equal to standard deviation     
        for geohash, trip_difference in trip_data:
            if geohash != None:
                if trip_difference >= float(self.d_std2[geohash]):
                    yield None, row

if __name__ == '__main__':
    MRFilterTrips.run()