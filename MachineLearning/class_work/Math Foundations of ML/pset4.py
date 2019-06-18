import numpy as np

def gramSchmidt(X):
    '''
    Takes list of lists X as input. Returns np array U as output
    '''
    Xt = list(np.transpose(X))
    for n, Xi in enumerate(Xt):
        if all(i == 0 for i in list(Xi)):
            del Xt[n]
    U = []
    for n, Xi in enumerate(Xt):
        if n > 0:
            sum_residual = 0
            for j in range(n):
                sum_residual = np.add(sum_residual, np.matmul(U[j], Xi) * np.transpose(U[j]))
            Xi = np.subtract(Xi, sum_residual)
        size = np.sqrt(np.sum([i** 2 for i in Xi]))
        if size > 1e-10:
            Ui = Xi / size
        else:
            Ui = np.zeros(len(Xi))
        U.append(Ui)
    U = list(U)
    for n, Ui in enumerate(U):
        if all(i == 0 for i in list(Ui)):
            del U[n]
    return np.transpose(U)
