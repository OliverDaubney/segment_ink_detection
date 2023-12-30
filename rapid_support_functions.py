"""
A set of functions to support segment ink detection.
"""

import random
import numpy as np


# FUNCTIONS TO SUPPORT THE DEPTH SCAN PROCESS.
def get_random_point(arr, y_min, y_max, x_min, x_max):
    """
        A basic function to return a random point from
        a given array as long as the point value is not
        equal to zero.
    """
    while True:
        y = random.randint(y_min, y_max)
        x = random.randint(x_min, x_max)
        if arr[y, x] != 0:
            return arr[y, x]
            

# FUNCTIONS TO SUPPORT THE INK DETECTION PROCESS.
def create_sub_volume(x, y, images):
    """
        A function to create an 8x65x65 sub-volume from
        a stack of images that can be passed to the ink
        detection model.
    """
    img_stack = images[0:8, y-32:y+33, x-32:x+33]
    return img_stack

def grid_update(grid, i, j, cell_avg, n):
    """
        A function to insert an n×n grid with a set value
        into a larger grid, then return the larger grid.
    """
    grid_insert = np.full((n, n), cell_avg, dtype='float32')
    grid[i:i+n, j:j+n] = grid_insert
    return grid

