'''
CMSC 12300 Spring 2018

Taxi Trips Project
Madeline Kim, Maya Roberts, Edwin Gavis, Mike Gu
'''

from mrjob.job import MRJob
import csv

'''
Map reduce function to run through csv file to calculate intersections of lines
drawn between origin and destination coordinates of taxi trips. Every trip will
be compared against all other trips to calculate the intersection of their lines
if an intersection can be found.

Outputs line by line a pair of coordinates (intersection) as key with frequency
as value
'''
class MRIntersections(MRJob):
	# Gather second csv into list
	def mapper_init(self):
		with open('/Volumes/MADELINE/project/Taxi_Trips2.csv') as csvfile:
			csv_reader = csv.reader(csvfile)
			self.full_set = list(csv_reader)
		csvfile.close()

	def mapper(self, _, line):
		for row in csv.reader([line]):
			trip_id = row[0]
			# Store coordinates as floats
			try:
				pickup_y1 = float(row[17])
				pickup_x1 = float(row[18])

				dropoff_y1 = float(row[20])
				dropoff_x1 = float(row[21])
			except ValueError:
				pass
			else:
				line_params1 = make_line_params(pickup_x1, pickup_y1, 
					dropoff_x1, dropoff_y1)

				'''
				 Loop through duplicate csv file to compare given trip to all
				 other trips
				'''
					#firstline = True
				for row2 in self.full_set:
						#Store coordinates as floats in given row of duplicate
						#file 
					try:
						pickup_y2 = float(row2[17])
						pickup_x2 = float(row2[18])

						dropoff_y2 = float(row2[20])
						dropoff_x2 = float(row2[21])

					except ValueError:
						continue

					line_params2 = make_line_params(pickup_x2, pickup_y2, 
					dropoff_x2, dropoff_y2)

						# Check if same trip ID (avoid calculation for duplicate)
					if row[0] == row2[0]:
						continue
						# Check if lines are parallel or same
					elif (line_params1['a'] * line_params2['b'] - \
						line_params1['b'] * line_params2['a'] == 0):
						continue
					else:
						yield line_intersect(line_params1, line_params2), 1

	def combiner(self, coords, counts):
		yield coords, sum(counts)

	def reducer(self, coords, counts):
		total = sum(counts)
		# Handle duplicate calculations, as intersections between any 2 trips
		# are calculated twice (trip1 -> trip2, trip2 -> trip1)
		try:
			new_coords = coords.split(',')

			# Separate out coordinates
			new_coords[0] = float(new_coords[0])
			new_coords[1] = float(new_coords[1])

			# Filter out coordinates well outside of Chicago, excluding those in lake
			if (new_coords[0] > -87.666025 and new_coords[0] < -87.522251) and \
				(new_coords[1] > 41.639517 and new_coords[1] < 41.972081):
				if total % 2 == 0:
					yield coords, total / 2
				else:
					yield coords, total
		except:
			pass

	# def steps(self):
	#     return [
	#  		MRStep(mapper=self.mapper_init),
	#  		MRStep(mapper=self.mapper,
	#              combiner=self.combiner,
	#              reducer=self.reducer)
	#     ]

'''
Calculate line equation coefficients a,b,c (ax + by = c)
Receives four values: x1, y1, x2, y2 where (x1, y1) and (x2, y2) represent
coordinates of points 1 and 2
Output: linear coefficients a,b,c in format {'a': a, 'b': b, 'c': c}
'''
def make_line_params(x1, y1, x2, y2):
	# Check parameters are numerical
	param_error = False
	try:
		x1 = float(x1)
	except ValueError:
		print("Error(make_line_params): x1 is not numerical")
		param_error = True

	try:
		x2 = float(x2)
	except ValueError:
		print("Error(make_line_params): x2 is not numerical")
		param_error = True
	
	try:
		y1 = float(y1)
	except ValueError:
		print("Error(make_line_params): y1 is not numerical")
		param_error = True

	try:
		y2 = float(y2)
	except ValueError:
		print("Error(make_line_params): y2 is not numerical")
		param_error = True

	if param_error:
		return {'slope': None, 'y_int': None}

	a = x2 - x1
	b = y2 - y1
	c = (x2 * y1) - (x1 * y2) 
	return {'a': a, 'b': b, 'c': c}

''' 
Solve linear system of equations with Cramer's rule:
(https://en.wikipedia.org/wiki/Cramer%27s_rule)
Receives lines in form of {'a': a, 'b': b, 'c': c}, where ax + by = c
Output x, y pair in tuple format (x, y)
'''
def line_intersect(line1, line2):
	#if (slope1 % slope2 == 0 ) or (slope2 % slope1 == 0 ):
	if line1['a'] * line2['b'] - line1['b'] * line2['a'] == 0:
		print('Lines are parallel or are same, cannot find intersection')
		return None, None

	# Calculate y coordinate
	y = ((line1['c'] * line2['b']) - (line1['b'] * line2['c'])) / \
		((line1['a'] * line2['b']) - (line1['b'] * line2['a']))

	# Calculate x coordinate
	x = -(((line1['a'] * line2['c']) - (line1['c'] * line2['a'])) / \
			((line1['a'] * line2['b']) - (line1['b'] * line2['a'])))

	return str(x) + "," + str(y)

	return str(x) + "," + str(y)

'''
Combine functions make_line_params and line_intersect to calculate intersection
from four sets of coordinates.

Input: 4 tuples of floats (x, y coordinates)
Output: Coordinates of ntersection (tuple of floats)
'''
# def coords_to_intersect(orig_point1, dest_point1, orig_point2, dest_point2):
#   line1 = make_line_params(orig_point1[0], orig_point1[1], dest_point1[0],
#       dest_point1[1])
#   line2 = make_line_params(orig_point2[0], orig_point2[1], dest_point2[0],
#       dest_point2[1])
#   return line_intersect(line1, line2)

if __name__ == '__main__':
	MRIntersections.run()
