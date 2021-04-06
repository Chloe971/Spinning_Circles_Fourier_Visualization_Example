import matplotlib
from matplotlib import animation, rc
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
from IPython.display import HTML
import numpy as np
from PIL import Image, ImageEnhance
import requests
from io import BytesIO
from copy import deepcopy
from scipy.spatial import distance
from scipy.interpolate import UnivariateSpline
from copy import deepcopy

class FourierTransform : 

    # Calculate the complex Fourier coeffiients for a given function

    def __init__(self, fxn, rnge, N = 500, period = None, num_points = 1000, num_circles = 50) :
    # fxn : Function to be transformed (as Python function object)
    # rnge : (.,.) tuple of range at which to evaluate fxn
    # N : Number of coefficients to calculate
    # period : f different than full length of function
    # num_points : Number of points at which to evalute function
    # num_circles : This is needed to calculate proper offsets

        self.num_circles = num_circles

        t_vals, y = zip(*[(v, fxn(v)) for v in np.linspace(rnge[0], rnge[1] - 1, num_points)])
        t_vals = np.array(t_vals)
        self.t_vals = t_vals

        # Save the original coords wheen plotting
        y = np.array(y)
        y = y - y[0]
        self.fxn_vals = np.array(deepcopy(y))

        # Spline function doesn't make endpoints exactly equal
        # This sets the firts and last points to their averagee
        endpoint = np.mean([y[0], y[-1]])
        y[0] = endpoint
        y[-1] = endpoint

        # Transform works best around edges when function starts at zero
        y = y - y[0]
        self.N = N

        if period == None :
            period = rnge[1]

        self.period = period


        def Cn(n) : 
            c = y * np.exp(-1j * 2 * n * np.pi * t_vals/period)
            return (c.sum()/c.size)

        
        coefs = [Cn(i) for i in range(1, N+1)]

        self.coefs = coefs
        self.real_coefs = [c.real for c in self.coefs]
        self.imag_coefs = [c.imag for c in self.coefs]

        self.amplitudes = np.absolute(self.coefs)
        self.phases = np.angle(self.coefs)


        def f(x, degree = N) :
            #Evaluate the function y at time t using Fourier approximation of degree N
            f = np.array([2 * coefs[i -1] * np.exp(1j * 2 * i * np.pi * x/period) for i in range(1, degree)])
            return(f.sum())


        #Evaluate function at all specified points in t domain
        fourier_approximation = np.array([f(t, degree = N).real for t in t_vals])
        circles_approximation  = np.array([f(t, degree = self.num_circles).real for t in t_vals])

        # Set intercept to same as original function
        # fourier_approximation = fourier_approximation - fourier_approximation[0] + self.original_offset

        fourier_approximation = fourier_approximation - (fourier_approximation - self.fxn_vals).mean()

        circles_approximation = circles_approximation - (circles_approximation - self.fxn_vals).mean()
        self.circles_approximation = circles_approximation

        # Origin offset
        self.origin_offset = fourier_approximation[0] - self.fxn_vals[0]

        # Circles offset
        self.circles_approximation_offset = circles_approximation[0] - self.fxn_vals[0]

        # Set intercept to same as original function
        self.fourier_approximation = fourier_approximation