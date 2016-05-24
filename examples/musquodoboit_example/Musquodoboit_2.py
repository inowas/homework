import os
import numpy as np
import matplotlib.pyplot as plt
import flopy.modflow as mf
import flopy.utils as fu
import shutil
import matplotlib.colors as mc
import pprint

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

workspace = os.path.join('ascii')
output = os.path.join('output')

# delete directories if existing
if os.path.exists(workspace):
    shutil.rmtree(workspace)

if os.path.exists(output):
    shutil.rmtree(output)

if not os.path.exists(workspace):
    os.makedirs(workspace)

if not os.path.exists(output):
    os.makedirs(output)

# flopy objects
modelname = 'Musquodoboit'
m = mf.Modflow(modelname=modelname, exe_name='mf2005', model_ws=workspace)

# model domain and grid definition
ztop = 0.  # top of layer ft
botm = -10.  # bottom of layer ft
nlay = 1  # number of layers (z)
nrow = 44  # number of rows (y)
ncol = 55  # number of columns (x)
Lx = 5500 # length of x model domain, in ft
Ly = 4400 # length of y model domain, in ft
delr = Lx / ncol  # row width of cell, in ft
delc = Ly / nrow  # column width of cell, in ft
delv = (ztop - botm) / nlay #  vertical width of cell, in ft


# define the stress periods
nper = 1
nstp = 10  # number of time steps
perlen = 0.12960e+06  # length of simulation, in seconds
steady = False  # steady state or transient

dis = mf.ModflowDis(m, nlay, nrow, ncol, delr=delr, delc=delc, top=ztop, botm=botm, nper=nper, perlen=perlen, nstp=nstp, steady=steady, itmuni=1, lenuni=1,tsmult=1.414,)


def line_area_intersect(line, xmax, xmin, ymax, ymin, nx, ny):
    """
    
    """
    line_cols = []
    line_rows = []
    dx = (xmax - xmin)/nx
    dy = (ymax - ymin)/ny
    #Converting line values to floats
    for i, point in enumerate(line):
        for j, xy in enumerate(point):
            line[i][j] = float(xy)
    
    for i in range(len(line) - 1):
        strt_x = line[i][0]
        end_x = line[i + 1][0]
        strt_y = line[i][1]
        end_y = line[i + 1][1]

        strt_col = int((strt_x - xmin)/(xmax - xmin) * (nx)) if strt_x < xmax else int((strt_x - xmin)/(xmax - xmin) * (nx)) - 1
        end_col = int((end_x - xmin)/(xmax - xmin) * (nx)) if end_x < xmax else int((end_x - xmin)/(xmax - xmin) * (nx)) - 1
        strt_row = int((strt_y - ymin)/(ymax - ymin) * (ny)) if strt_y < ymax else int((strt_y - ymin)/(ymax - ymin) * (ny)) - 1 
        end_row = int((end_y - ymin)/(ymax - ymin) * (ny)) if end_y < ymax else int((end_y - ymin)/(ymax - ymin) * (ny)) - 1

        steep = abs(strt_y - end_y) >= abs(strt_x - end_x)

        if steep:
            strt_y, strt_x = strt_x, strt_y
            end_y, end_x = end_x, end_y
            strt_col, strt_row = strt_row, strt_col
            end_col, end_row = end_row, end_col
            dy, dx = dx, dy
            xmin, ymin = ymin, xmin
        slope = (end_y - strt_y)/(end_x - strt_x)  
        upwards = abs(strt_y) <= abs(end_y)
        forward = abs(strt_x) <= abs(end_x)

        strt_bx = xmin + (strt_col + 1) * dx if forward else xmin + (strt_col) * dx
        strt_by = ymin + (strt_row + 1) * dy if upwards else ymin + (strt_row) * dy
        segment_rows = []
        segment_cols = []
        segment_cols.append(strt_col)
        segment_rows.append(strt_row)
        j = 0
        for i in range(abs(end_col - strt_col)):
            y = strt_y + slope * (strt_bx + dx * i - strt_x) if forward else strt_y + slope * (strt_bx - dx * i - strt_x)
            crossed = y >= strt_by + dy * j if upwards else y <= strt_by - dy * j
            if crossed:
                col = strt_col + i if forward else strt_col - i
                segment_cols.append(col)
                col = strt_col + (i + 1) if forward else strt_col - (i + 1) 
                segment_cols.append(col)
                row = strt_row + (j + 1) if upwards else strt_row - (j + 1)
                segment_rows.append(row)
                segment_rows.append(row)
                j += 1
            else:
                col = strt_col + (i + 1) if forward else strt_col - (i + 1)
                segment_cols.append(col)
                row = strt_row + j if upwards else strt_row - j
                segment_rows.append(row)

        if segment_rows[-1] != end_row or segment_cols[-1] != end_col:
            segment_cols.append(end_col)
            segment_rows.append(end_row)

        if steep:
            segment_cols, segment_rows = segment_rows, segment_cols
            xmin, ymin = ymin, xmin
            dx, dy = dy, dx

        if len(line_cols) < 1:
            line_cols += segment_cols
            line_rows += segment_rows
        else:
            line_cols += segment_cols[1:]
            line_rows += segment_rows[1:]

    return line_cols, line_rows

class Modelarea(object):
    """
    The model area with imorted and calcuated discretization parameters and active/inactive cells information
    """

    def __init__(self, nx, ny, xmin, xmax, ymin, ymax):

        self.nx = nx
        self.ny = ny
        self.xmin = xmin
        self.xmax =xmax
        self.ymin = ymin
        self.ymax = ymax
        self.dx = (self.xmax - self.xmin)/self.nx
        self.dy = (self.ymax - self.ymin)/self.ny
    
    def give_ibound(self, line, number_of_layers):
        """

        """
        self.line = line
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.line_cols, self.line_rows = line_area_intersect(line = self.line, xmax = self.xmax, xmin = self.xmin, ymax = self.ymax, ymin = self.ymin, nx = self.nx, ny = self.ny)
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        area_line_rows = np.ones(len(self.line_rows), dtype = np.int32) * (self.ny - 1) - np.array(self.line_rows)
        area_line_cols = np.array(self.line_cols)
        empty_rows = []
        empty_cols = []
        for i in range(self.ny):
            empty_cols += range(self.nx)
            empty_rows += [i] * self.nx
            #Lists of cols and rows to be removed from the entire list:

        rem_cols = []
        rem_rows = []
        for i in range(len(area_line_cols)):
            rem_cols.append(area_line_rows[i] * self.nx + area_line_cols[i])
            rem_rows.append(area_line_rows[i] * self.nx + area_line_cols[i])
        rem_rows = list(set(rem_rows))
        rem_cols = list(set(rem_cols))

        for i in sorted(rem_cols, reverse=True):
            del empty_cols[i]
        for i in sorted(rem_rows, reverse=True):
            del empty_rows[i]

        inner_cell_idx = []
        for i in range(len(empty_rows)):
            x = (self.xmin + empty_cols[i] * self.dx) + self.dx/2
            y = (self.ymax - empty_rows[i] * self.dy) - self.dy/2
            crossed = 0
            for j in range(len(self.line) - 1):
                crossed_segment_up =  y < self.line[j][1] and y > self.line[j+1][1]
                crossed_segment_down =  y > self.line[j][1] and y < self.line[j+1][1]
                crossed_point = y == self.line[j][1]
                
                if (crossed_segment_up or crossed_segment_down or crossed_point) and x < self.line[j][0] - ((self.line[j][1] - y)/(self.line[j][1] - self.line[j+1][1]) * (self.line[j][0] - self.line[j+1][0])):
                    crossed += 1
            if crossed % 2 == 0:
                inner_cell_idx.append(0)
            else:
                inner_cell_idx.append(1)
        self.ibound = np.zeros((int(number_of_layers), self.ny, self.nx), dtype=np.int32)
        for i in range(len(empty_rows)):
            self.ibound[:, empty_rows[i], empty_cols[i]] = inner_cell_idx[i]

        for i in range(len(area_line_rows)):
            self.ibound[:, area_line_rows[i], area_line_cols[i]] = 1
# If you want to set boundary cells to -1 or whatever change the ' = 1' above to number that you want
        return self.ibound
#######################################################################
       
nrow = 54
ncol = 44
nx, ny = ncol, nrow
xmin, xmax, ymin, ymax = 0., 45., 0., 54.

line = [[16.,0.],[14.,7.],[15.,14.],[8.,21.],[8.,25.],[0.,23.],[0.,24.],[5.,31.],[5.,35.],[7.,45.],[8.,50.],[11.,37.],[13.,37.],[16.,34.],[18.,36.],[21.,36.],[22.,35.],[23.,35.],[24.,43.],[23.,44.],[23.,50.],[27.,54.],[33.,48.],[35.,49.],[43.,40.],[44.,35.],[44.,34.],[42.,33.],[40.,32.],[40.,29.],[43.,25.],[44.,17.], [41.,15.],[44.,19.],[26.,17.],[16.,0.]]
MA = Modelarea(nx, ny, xmin, xmax, ymin, ymax)
ibound = MA.give_ibound(line, 1)
########
plt.imshow(ibound[0], interpolation = 'nearest')

# hydraulic parameters (aquifer properties with the bcf-package)
sf = 1 # storage coefficient
laycon = 0 # layer type, confined (0), unconfined (1), constant T, variable S (2), variable T, variable S (default is 3)
tran = [[
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,1,1,0,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 4,4,4,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,4,4,4,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,4,4,4,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,4,4,4,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,4,4,4,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,4,4,4,4,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,2,1,1,1,1,1,1,1,1,1,1,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,1,1,1,1,1,1,1,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,1,1,1,1,1,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,1,1,1,1,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,1,1,1,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,1,1,1,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,2,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,1,1,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,2,2,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,2,2,2,2,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,2,2,2,2,2,2,2,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,4,4,4,4,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]]
bcf = mf.ModflowBcf(m,sf1=sf, laycon=0, tran=tran)

# setting up the well package with stress periods
pumping_rate = -0.963 # ft^3 / s
lrcq = [[0, 28, 31, -5.963]]
wel = mf.ModflowWel(m, stress_period_data=lrcq)

# setting up the river package with stress periods
lrcd=[[0,  18-1,   1-1,  0.0, .02,  -10],
      [0,  18-1,   2-1,  0.0, .02,  -10],
      [0,  19-1,   3-1,  0.0, .02,  -10],
      [0,  19-1,   4-1,  0.0, .02,  -10],
      [0,  20-1,   5-1,  0.0, .02,  -10],
      [0,  20-1,   6-1,  0.0, .02,  -10],
      [0,  20-1,   7-1,  0.0, .02,  -10],
      [0,  21-1,   8-1,  0.0, .02,  -10],
      [0,  21-1,   9-1,  0.0, .02,  -10],
      [0,  22-1,  10-1,  0.0, .02,  -10],
      [0,  22-1,  11-1,  0.0, .02,  -10],
      [0,  22-1,  12-1,  0.0, .02,  -10],
      [0,  23-1,  13-1,  0.0, .02,  -10],
      [0,  23-1,  14-1,  0.0, .02,  -10],
      [0,  24-1,  15-1,  0.0, .02,  -10],
      [0,  24-1,  16-1,  0.0, .02,  -10],
      [0,  24-1,  17-1,  0.0, .02,  -10],
      [0,  24-1,  18-1,  0.0, .02,  -10],
      [0,  25-1,  19-1,  0.0, .02,  -10],
      [0,  25-1,  20-1,  0.0, .02,  -10],
      [0,  25-1,  21-1,  0.0, .02,  -10],
      [0,  25-1,  22-1,  0.0, .02,  -10],
      [0,  26-1,  23-1,  0.0, .02,  -10],
      [0,  26-1,  24-1,  0.0, .02,  -10],
      [0,  27-1,  25-1,  0.0, .02,  -10],
      [0,  27-1,  26-1,  0.0, .02,  -10],
      [0,  28-1,  27-1,  0.0, .02,  -10],
      [0,  28-1,  28-1,  0.0, .02,  -10],
      [0,  28-1,  29-1,  0.0, .02,  -10],
      [0,  28-1,  30-1,  0.0, .02,  -10],
      [0,  28-1,  31-1,  0.0, .02,  -10],
      [0,  27-1,  32-1,  0.0, .02,  -10],
      [0,  27-1,  33-1,  0.0, .02,  -10],
      [0,  27-1,  34-1,  0.0, .02,  -10],
      [0,  27-1,  35-1,  0.0, .02,  -10],
      [0,  28-1,  36-1,  0.0, .02,  -10],
      [0,  29-1,  37-1,  0.0, .02,  -10],
      [0,  29-1,  38-1,  0.0, .02,  -10],
      [0,  30-1,  39-1,  0.0, .02,  -10],
      [0,  30-1,  40-1,  0.0, .02,  -10],
      [0,  31-1,  41-1,  0.0, .02,  -10],
      [0,  31-1,  42-1,  0.0, .02,  -10],
      [0,  32-1,  43-1,  0.0, .02,  -10],
      [0,  32-1,  44-1,  0.0, .02,  -10],
      [0,  33-1,  45-1,  0.0, .02,  -10],
      [0,  33-1,  46-1,  0.0, .02,  -10],
      [0,  33-1,  47-1,  0.0, .02,  -10],
      [0,  33-1,  48-1,  0.0, .02,  -10],
      [0,  33-1,  49-1,  0.0, .02,  -10]]
      
riv = mf.ModflowRiv(m, stress_period_data=lrcd)

# instantiation of the solver with default values
pcg = mf.ModflowPcg(m) # pre-conjugate gradient solver

# instantiation of the output control with default values
oc = mf.ModflowOc(m) # output control

m.write_input()
m.run_model()

hds = fu.HeadFile(os.path.join(workspace, modelname+'.hds'))
h = hds.get_data(kstpkper=(9, 0))


# Output based on this example: http://matplotlib.org/mpl_toolkits/mplot3d/tutorial.html#surface-plots
fig = plt.figure()
ax = fig.gca(projection='3d')
X = np.linspace(0, Lx, ncol)
Y = np.linspace(0, Ly, nrow)
X, Y = np.meshgrid(X, Y)
Z = h[0]  # set layer 1
Z[Z < -900] = -5 # set all no-flow values to -5 -> a dirty hack until we find something nicer
ax.set_xlabel('length')
ax.set_ylabel('width')
ax.set_zlabel('height')

norm = mc.Normalize(vmin=0, vmax=1, clip=False)  # set min/max of the colors
surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.BrBG, linewidth=0.05, antialiased=False, norm=norm)
ax.set_zlim(-5, 0)  # set limit of z-axis
ax.xaxis.set_major_locator(LinearLocator(3))
ax.yaxis.set_major_locator(LinearLocator(3))
ax.zaxis.set_major_locator(LinearLocator(4))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
fig.colorbar(surf, shrink=0.7, aspect=10)
plt.savefig('/users/Alexey/desktop/descopgrid_rain.png')
plt.show()