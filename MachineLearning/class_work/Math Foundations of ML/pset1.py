'''
1e.
'''

import numpy as np

resource_mat = np.ndarray.transpose(np.array([[1,1,0,0,0],[1,1,1,1,0],[0,0,2,0,3],[0,0,1,1,1]]))
cost_mat = np.ndarray.transpose(np.array([2,1,5,3,8]))
harrelson_mat = np.ndarray.transpose(np.array([6,2,1,0]))

#b result
b = np.matmul(cost_mat, resource_mat)
print("b.", b)

#c result
c = np.matmul(resource_mat, harrelson_mat)
print("c.", c)

#d result
d = np.matmul(c, cost_mat)
print("d.", d)
