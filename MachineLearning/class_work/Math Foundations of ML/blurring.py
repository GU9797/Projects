import numpy as np
import matplotlib.pyplot as plt

## deblurring

n = 500
k = 30
sigma = 0.01

# generate random piecewise constant signal
w = np.zeros((n, 1))
w[0] = np.random.standard_normal()
for i in range(1, n):
    if np.random.rand(1) < 0.95:
        w[i] = w[i-1]
    else:
        w[i] = np.random.standard_normal()


# generate k-point averaging function
h = np.ones(k) / k

# make a matrix for blurring
m = n + k - 1
X = np.zeros((m, m))
for i in range(m):
    if i < k:
        X[i, :i+1] = h[:i+1]
    else:
        X[i, i - k: i] = h

X = X[:, 0:n]

# blurred signal + noise
y = np.dot(X, w) + sigma*np.random.standard_normal(size=(m, 1))

# plot
f, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title('signal')
ax1.plot(w)
ax2.set_title('blurred and noisy version')
ax2.plot(y[0:n])

plt.show()
