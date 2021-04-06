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



class ComplexCircles:
    """Complex Circles Class:
        Tracks radii and centers of circles implied by 
        Fourier decomposition of given FourierTransform object
    """
    def __init__(self,
                 FT, # FourierTransform object
                 num_circles=20, # Number of circles to keep track of
                 t_init=0, # Initial time state of object
                 origin=(0, 0) # Center of the first circle
        ):
        self.FT = FT
        self.t_init = t_init
        if num_circles > FT.N:
            raise Exception("num_circles exceeds the degree of the given Fourier series.")
        self.num_circles = num_circles
        self.origin = origin
        self.origin_x = origin[0]
        self.origin_y = origin[1]
        self.t_elapsed = 0
        self.steps_elapsed = 0
        self.t_current = self.t_init
        self.t_index_current = 0
        self.true_fxn_val_current = self.FT.fxn_vals[t_init]
        self.fourier_approx_val_current = self.FT.fourier_approximation[t_init]
        
        self.Xs = [] # Track the coords of the center of the last circle
        self.Ys = [] # for each value of t 
        
        self.As = FT.amplitudes[0:num_circles] # Amplitude of each frequency/circle
        self.Zs = FT.phases[0:num_circles] # Phase of each frequency/cirlce
    
    def circle_positions(self, transpose=False):
        """compute the current radii and centers of each circle at the current value of t"""
        
        num_circles = self.num_circles
        t = self.t_current
        
        running_x_offset = deepcopy(self.origin_x)
        running_y_offset = deepcopy(self.origin_y)

        # There will be 1 more center than radius;
        # Use this to plot the last point on the last circle
        # Stored in final_x, final_y below
        radii = []
        x_centers = [deepcopy(self.origin_x)]
        y_centers = [deepcopy(self.origin_y)]
        
        for i in range(0,num_circles):
            freq = i+1 # Corresponding frequency for given circle/coefficient
            a = self.As[i] # Magnitude (i.e., amplitude) of complex coefficient
            z = self.Zs[i] # Argument (i.e., phase) of complex coefficient

            radius = 2*a
            radii.append(radius)
            
            running_x_offset += 2*a*np.cos(t*2*np.pi*freq/self.FT.period + z)
            running_y_offset += 2*a*np.sin(t*2*np.pi*freq/self.FT.period + z)
            
            if i < num_circles-1:
                x_centers.append(running_x_offset)
                y_centers.append(running_y_offset)
            
        if t==0:
            self.circles_offset = running_x_offset
        radii = np.array(radii)
        x_centers = np.array(x_centers) - self.circles_offset + self.FT.origin_offset
        y_centers = np.array(y_centers)
        
        x_final = running_x_offset - self.circles_offset + self.FT.origin_offset
        y_final = running_y_offset
        
        self.Xs.append(x_final)
        self.Ys.append(y_final)
        
        if transpose:
            return(radii, -y_centers, x_centers, -y_final, x_final)
        return(radii, x_centers, y_centers, x_final, y_final)
    
    
    def get_circles(self, transpose=False):
        return(self.circle_positions(transpose=transpose))
    
    def step(self, dt=1):
        # dt = how many times to increment t_vals array for each step
        self.steps_elapsed += 1
        next_index = dt*self.steps_elapsed 
        if next_index > len(self.FT.t_vals)-1:
            print("Max t-value reached")
            self.steps_elapsed -= 1
        else:
            self.t_current = self.FT.t_vals[next_index]
            self.t_elapsed = self.t_current - self.t_init
            self.t_index_current = next_index
            self.true_fxn_val_current = self.FT.fxn_vals[next_index]
            self.fourier_approx_val_current = self.FT.fourier_approximation[next_index]