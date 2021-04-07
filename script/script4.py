from matplotlib import animation, rc
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
import numpy as np
from scipy.spatial import distance
from IPython.display import HTML
from copy import deepcopy
from matplotlib.animation import FuncAnimation, PillowWriter


#Our previously defined package
import Package
from Package import ImageObject
from Package import FourierTransform
from Package import ComplexCircles

#Step 1 : Package ImageManipulation

__file__ = "script.py"
url = "https://archzine.fr/wp-content/uploads/2018/11/femme-dessin-comment-dessiner-un-chien-dessin-facile-a-faire-beau-dessin-simple-a-faire-connaitre-les-lignes-qui-creent-l-image.jpg"
horse = Package.ImageObject(url)


#Step 2 : Package FourierTransform

# Calculate Fourier approximations; initialize NC equal to the
# number of circles the final animation will have to get an 
# accurate view of how well the image will be approximated
NC = 50
xFT = FourierTransform(horse.x_spl, (0, horse.num_pixels), num_circles=NC)
yFT = FourierTransform(horse.y_spl, (0, horse.num_pixels), num_circles=NC)

# Plot the full approximation and the NC-degree 
# approximation for t from 1-R
R = 50
plt.plot(xFT.t_vals[0:R], xFT.fxn_vals[0:R])
plt.plot(xFT.t_vals[0:R], xFT.fourier_approximation[0:R], "--")
plt.plot(xFT.t_vals[0:R], xFT.circles_approximation[0:R], ".-")

plt.plot(yFT.t_vals[0:R], yFT.fxn_vals[0:R])
plt.plot(yFT.t_vals[0:R], yFT.fourier_approximation[0:R], "--")
plt.plot(yFT.t_vals[0:R], yFT.circles_approximation[0:R], ".-")

# Visualize the approximation as 2D image
plt.plot(xFT.fxn_vals, yFT.fxn_vals)
plt.plot(xFT.fourier_approximation, yFT.fourier_approximation)
plt.plot(xFT.fourier_approximation[0], yFT.fourier_approximation[0], 'o', color='red')


#Step 3 : Visualization + Package PositionCalculate
x_spl = horse.x_spl
y_spl = horse.y_spl
num_pixels = horse.num_pixels

# Number of circles to draw in animation
num_circles = 100

anim_length = 20 # in seconds
fps = 24 # frames per second
num_frames = anim_length*fps
interval = (1./fps)*1000

# Ensure that the approximation has at least 2000
# points to ensure smoothness
dt = (int(2000. / num_frames) + 1)
num_points =  dt* num_frames
xFT = FourierTransform(x_spl, (0, num_pixels), num_points=num_points, N=num_circles)
yFT = FourierTransform(y_spl, (0, num_pixels), num_points=num_points, N=num_circles)

# Distance between circles and image
X_circles_spacing = 200
Y_circles_spacing = 300

# Origin calculation: Offset the circles so they line up with 
# the plotted image
x_main_offset = xFT.origin_offset
y_main_offset = yFT.origin_offset
x_origin = (0, X_circles_spacing)
#y_origin = (circles_spacing, y_main_offset)
y_origin = (0, Y_circles_spacing)
#y_origin = (0,0)

# These calculations set transparency based on how close the 
# approximation is to the original function (prevents the big 
# swoops across the drawing to dominate the image)
approx_coords = np.array(list(zip(xFT.fourier_approximation, yFT.fourier_approximation)))
og_coords = np.array(list(zip(horse.x_tour, horse.y_tour)))
approx_dist = distance.cdist(approx_coords, og_coords, 'euclidean')
closest_points = approx_dist.min(1)
def alpha_fxn(d):
    # Takes distance between approx. and true value
    # and returns transparency level
    return(np.exp(-(1/10)*d))
    #hist = plt.hist(closest_points)
    heights = hist[0]
    scaled_h = heights/heights[0]
    breaks = hist[1]
    for i, b in enumerate(breaks[1:]):
        if d < b:
            return(scaled_h[i])
    
cutoff = int(len(closest_points)*.95)
alpha_vals = [ alpha_fxn(p) if i < cutoff else 0.33 for i, p in enumerate(closest_points) ]

xCircles = ComplexCircles(xFT, num_circles=num_circles, origin=x_origin)
yCircles = ComplexCircles(yFT, num_circles=num_circles, origin=y_origin)

#------------------------------------------------------------
# set up figure and styling
fig = plt.figure()
plt.axis([-400,75,-150,350])

ax = plt.gca()
ax.set_aspect(1)
ax.set_facecolor('#f9f9f9')

# Suppress axes
ax.set_yticklabels([])
#ax.set_xticklabels([])
plt.tight_layout(pad=0)
plt.axis('off')

circle_color = 'black'
drawing_color = '#9c0200'


#------------------------------------------------------------
# Set up animation elements


# INITIALIZE CIRLCE PLOTS
alphas = np.linspace(1, 0.25, num_circles) #np.repeat(1, num_circles)
X_circle_objs = []
X_center_objs = []
Y_circle_objs = []
Y_center_objs = []

X_radii, X_x_centers, X_y_centers, X_x_final, X_y_final = xCircles.get_circles()
Y_radii, Y_x_centers, Y_y_centers, Y_x_final, Y_y_final = yCircles.get_circles(transpose=True)


for c in range(0,num_circles):
    # X Outer Circles
    Xcirc = plt.Circle((X_x_centers[c], X_y_centers[c]), radius=X_radii[c],
                      edgecolor=circle_color, facecolor='None', alpha=alphas[c])
    X_circle_objs.append(Xcirc)
    # X Center Point Circles
    Xcenter = plt.Circle((X_x_centers[c], X_y_centers[c]), radius=2,
                      edgecolor=circle_color, facecolor=circle_color, alpha=alphas[c])
    X_center_objs.append(Xcenter)
    
    
    # Y Outer Circles
    Ycirc = plt.Circle((Y_x_centers[c], Y_y_centers[c]), radius=Y_radii[c],
                      edgecolor=circle_color, facecolor='None', alpha=alphas[c])
    Y_circle_objs.append(Ycirc)
    # Y Center Point Circles
    Ycenter = plt.Circle((Y_x_centers[c], Y_y_centers[c]), radius=2,
                      edgecolor=circle_color, facecolor=circle_color, alpha=alphas[c])
    Y_center_objs.append(Ycenter)

    
# Connectors between end of circles and actual drawing
X_connector_line, = ax.plot([], [], '-', lw=1, color='black')
Y_connector_line, = ax.plot([], [], '-', lw=1, color='black') 

# Point on plot at current time t
trace_point, = ax.plot([], [], 'o', markersize=8, color=drawing_color)

# Trace of full drawing
drawing_segments = []
for idx in range(len(xFT.t_vals)):
    segment, = ax.plot([-1000, -1001], [-1000,-1001], '-', lw=1, color=drawing_color, alpha=alpha_vals[idx])
    drawing_segments.append(segment)
# Add one more for line segment
segment, = ax.plot([-1000,-1001], [-1000,-1001], '-', lw=1, color=drawing_color, alpha=alpha_vals[0])
drawing_segments.append(segment)


# Plot axes of cirlces
x_main_offset = X_x_centers[0]
y_main_offset = Y_y_centers[0]

axis_length = 50
axis_style = {
    "linestyle": "solid",
    "linewidth": 1,
    "color": "black"
}
x_x_axis = ax.plot(
    [x_main_offset-axis_length, x_main_offset+axis_length], 
    [X_circles_spacing,X_circles_spacing],
    **axis_style
)
x_y_axis = ax.plot(
    [x_main_offset, x_main_offset], 
    [X_circles_spacing-axis_length,X_circles_spacing+axis_length],
    **axis_style
)
y_x_axis = ax.plot(
    [-Y_circles_spacing-axis_length, -Y_circles_spacing+axis_length],
    [y_main_offset, y_main_offset], 
    **axis_style
)
y_y_axis = ax.plot(
    [-Y_circles_spacing, -Y_circles_spacing],
    [y_main_offset-axis_length, y_main_offset+axis_length], 
    **axis_style
)


def init():
    """initialize animation"""
    for idx in range(len(xFT.t_vals)):
        drawing_segments[idx].set_data([],[])
    
    X_connector_line.set_data([], [])
    Y_connector_line.set_data([], [])
    trace_point.set_data([], [])
    #centers.set_data([], [])
    for c in range(num_circles):
        ax.add_patch(X_circle_objs[c])
        ax.add_patch(X_center_objs[c])
        ax.add_patch(Y_circle_objs[c])
        ax.add_patch(Y_center_objs[c])
    return([])

def animate(i):
    """perform animation step"""
        
    X_radii, X_x_centers, X_y_centers, X_x_final, X_y_final = xCircles.get_circles()
    Y_radii, Y_x_centers, Y_y_centers, Y_x_final, Y_y_final = yCircles.get_circles(transpose=True)
    #Y_x_centers = [x - circles_spacing for x in Y_x_centers]
    #Y_x_final = Y_x_final - circles_spacing

    
    for c in range(0,num_circles):
        # X Outer Circles
        X_circle_objs[c].center = (X_x_centers[c], X_y_centers[c])
        # X Center Point Circles
        X_center_objs[c].center = (X_x_centers[c], X_y_centers[c])

        # Y Outer Circles
        Y_circle_objs[c].center = (Y_x_centers[c], Y_y_centers[c])
        # Y Center Point Circles
        Y_center_objs[c].center = (Y_x_centers[c], Y_y_centers[c])
        
    
    #idx_current = max(int(np.round(xCircles.t_current)),len(xFT.fourier_approximation)-1)
    idx_current = xCircles.t_index_current
    x_true_current = deepcopy(xCircles.fourier_approx_val_current)
    y_true_current = deepcopy(yCircles.fourier_approx_val_current)
    X_connector_line.set_data(
        [x_true_current, x_true_current], 
        [y_true_current, X_y_final]
    )
    Y_connector_line.set_data(
        [Y_x_final, x_true_current], [y_true_current, y_true_current]
    )
    trace_point.set_data([x_true_current], [y_true_current])
    
    # Iterate circles to next step
    xCircles.step(dt=dt)
    yCircles.step(dt=dt)

    drawing_segments[idx_current].set_data(
        [x_true_current, xCircles.fourier_approx_val_current], 
        [y_true_current, yCircles.fourier_approx_val_current]
    )

    
    return([])


ani = animation.FuncAnimation(fig, animate, frames=num_frames,
                              interval=interval, blit=True, init_func=init)


rc('animation', html='html5')
writer = PillowWriter(fps=25)  
ani.save("face1.gif", writer=writer)

# Fun miscellaneous function to draw a single frame of the 
# circles animation; understanding this step and getting the
# phase/amplitude of the circles correct is 90% of the work
# for understanding how the full animation works
def draw_circles(FT, t, num_circles=200):
    
    period = FT.period
    As = FT.amplitudes[0:num_circles]
    Zs = FT.phases[0:num_circles]

    t_vals = np.linspace(0,3000, 500)
    Xs = []
    Ys = []
    
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    
    x_offset = 0
    y_offset = 0

    col="#004785"
    
    for i in range(0,num_circles):
        Hz = i+1
        a = As[i] # Magnitude (i.e., amplitude) of complex coefficient
        z = Zs[i] # Argument (i.e., phase) of complex coefficient

        plt.plot([x_offset], [y_offset], marker='o', markersize=10, color=col)
        circ = plt.Circle((x_offset, y_offset), radius=2*a, edgecolor='black',
                          linewidth=2, facecolor='None')
        ax.add_patch(circ)

        x_offset += 2*a*np.cos(t*2*np.pi*Hz/period + z)
        y_offset += 2*a*np.sin(t*2*np.pi*Hz/period + z)

    Xs.append(x_offset)
    Ys.append(y_offset)
    plt.axis('equal')
    plt.show()
    return(fig)
f = draw_circles(xFT, 1400, num_circles=20)