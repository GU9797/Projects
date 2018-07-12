'''
CMSC 12300 Spring 2018

Taxi Trips Project
Madeline Kim, Maya Roberts, Edwin Gavis, Mike Gu
'''

import csv
import random
import sys

'''
This script samples rows from a given csv file given user-defined parameters

From command line:
	flags:
	--sample-size : number of rows to sample
	--input_csv : csv file to sample
	--output_csv : name of output file

arguments:
	sys.argv[1] : --sample-size
	sys.argv[2] : sample size (integer)
	sys.argv[3] : --input_csv
	sys.argv[4] : path to input csv file
	sys.argv[5] : --csv-length
	sys.argv[6] : length of csv file (range to sample from)
	sys.argv[7] : --output-csv
	sys.argv[8] : desired filename of output csv file

output: csv file with user-defined filename, rows sampled randomly from the 
		input file

Example:

python make_data_sample.py --sample-size 100 --input_csv taxi_trips_short.csv 
	--csv-length 200 --output-csv sampled_data.csv

'''
def main():

	# Check command line arguments
	if sys.argv[1] != "--sample-size":
		print("Error(make_sample_data): --sample-size flag required (e.g. --sample-size 4")
		exit(1)

	try:
		NUM_SAMPLE_ROWS = int(sys.argv[2])
		if NUM_SAMPLE_ROWS < 0:
			print("Error(make_sample_data): sample size must be non-negative integer")
			exit(1)
	except:
		print("Error(make_sample_data): sample size must be non-negative integer")
		exit(1)

	if sys.argv[3] != "--input_csv":
		print("Error(make_sample_data): --input_csv flag required (e.g. --csvfile data.csv")
		exit(1)

	if sys.argv[5] != "--csv-length":
		print("Error(make_sample_data): --csv-length flag required (e.g. --csv-length 200")
		exit(1)

	try:
		CSV_LENGTH = int(sys.argv[6])
		if CSV_LENGTH < 0:
			print("Error(make_sample_data): csv length must be non-negative integer")
			exit(1)
	except:
		print("Error(make_sample_data): csv length must be non-negative integer")
		exit(1)

	if sys.argv[7] != "--output-csv":
		print("Error(make_sample_data): --output-csv flag required (e.g. --output-csv output.csv")
		exit(1)
	
	sample_indices = random.sample(range(1, CSV_LENGTH), NUM_SAMPLE_ROWS)
	sample_indices.sort()
	try:
		with open("taxi_trips_short.csv", "rb") as csv_input:
			csv_reader = csv.reader(csv_input)
			index_tracker = 0
			i = 0
			with open("sampled_data.csv", "w+") as csv_output:
				csv_writer = csv.writer(csv_output,  delimiter=',')
				for row in csv_reader:
					if i == 0:
						csv_writer.writerow(row)
					if i == sample_indices[index_tracker]:
						csv_writer.writerow(row)
						index_tracker = index_tracker + 1
					i = i + 1
	except:
		print("Error(make_sample_data): cannot open csv file")
		exit(1)

if __name__ == "__main__":
   main()
