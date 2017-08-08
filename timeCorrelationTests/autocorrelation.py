from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import sys 

# use this method -- autoCorrelate1 was used to verify the math was correct
def autoCorrelate1(data, Nmax = None, skipIndex = 0, verbose = False):
    '''
    verbose prints the percent done while running
    skipIndex skips a fixed number of indices during calculation--- 
    this should be used to insure simulations of different dt have 
    the same number of points in calculation 
    ''' 
    n = len(data)
    if Nmax is not None:
        n = Nmax     # total number of points desired 
    rho = np.zeros(n)
    mu = np.mean(data)

    percent_done = int(n/100 + 1)


    if skipIndex is not 0:
        for k in range(0, n):
            R = 0
            N = 0
            for t in range(0, len(data)-k, skipIndex):
                R = R + (data[t]-mu)*(data[t+k]-mu)
                N = N + (data[t]-mu)**2
            if verbose and k % percent_done == 0:
                print '{}% done...'.format(k/n*100)
            rho[k] = R/N
    
    else:
        for k in range(0, n):
            R = 0
            N = 0
            for t in range(0, len(data)-k):
                R = R + (data[t]-mu)*(data[t+k]-mu)
                N = N + (data[t]-mu)**2
            if verbose and k % percent_done == 0:
                print '{}% done...'.format(k/n*100)
            rho[k] = R/N

    return rho

# use this method -- autoCorrelate1 was used to verify the math was correct
def autoCorrelate2(data, Nmax = None, skipIndex = 1, verbose = False):
    '''
    verbose prints the percent done while running
    skipIndex skips a fixed number of indices during calculation---
    this should be used to insure simulations of different dt have
    the same number of points in calculation
    '''
    n = len(data)
    if Nmax is not None:
        n = Nmax     # total number of points desired
    rho = np.zeros(n)
    mu = np.mean(data)

    percent_done = int(n/100 + 1)

    data_minus_mu = data - mu
    for k in range(0, n):
        R = sum(data_minus_mu[0:len(data)-k:skipIndex]*data_minus_mu[k:len(data):skipIndex])
        N = sum((data_minus_mu**2)[0:len(data)-k:skipIndex])
        if verbose and k % percent_done == 0:
            print '{}% done...'.format(k/n*100)
        rho[k] = R/N
    return rho

if __name__ == "__main__":
    A = np.random.rand(1000)
    rho10 = autoCorrelate2(A, Nmax = 500, skipIndex = 10)
    rho0 = autoCorrelate2(A, Nmax = 500)
    rho5 = autoCorrelate2(A, Nmax = 500, skipIndex = 5) 
    l = len(A)

    plt.figure()
    plt.plot(rho10, 'k')
    plt.plot(rho0, 'b')
    plt.plot(rho5, 'r') 
    plt.xlabel('n')
    plt.ylabel('np.random.rand(n)')
    plt.title('Test graph')
    plt.xlabel(r'$\Delta t$ [s]')
    plt.ylabel(r'$\rho (\Delta t) $')

    plt.show()
