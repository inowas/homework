import numpy as np
import matplotlib.pyplot as plt


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
            empty_cols += range(self.ny)
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

        self.ibound = np.zeros((int(number_of_layers), self.nx, self.ny), dtype=np.int32)
        for i in range(len(empty_rows)):
            self.ibound[:, empty_rows[i], empty_cols[i]] = inner_cell_idx[i]
        for i in range(len(area_line_rows)):
            self.ibound[:, area_line_rows[i], area_line_cols[i]] = 1
# If you want to set boundary cells to -1 or whatever change the ' = 1' above to number that you want
        return self.ibound
#######################################################################
       
nx, ny = 100, 100
xmin, xmax, ymin, ymax = 0., 40., 0., 40.

line = [[5.,5.],[11.,25.], [35.,40.],[38.,10.],[5.,5.]]

MA = Modelarea(nx, ny, xmin, xmax, ymin, ymax)
ibound = MA.give_ibound(line, 1)

########
plt.imshow(ibound[0], interpolation = 'nearest')
