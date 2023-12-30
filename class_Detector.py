"""
A set of functions to support Rapid Ink Detection.
"""

import random
import numpy as np
import PIL.Image as Image
import rapid_support_functions as sf
from collections import deque
Image.MAX_IMAGE_PIXELS = None

class Detector:
    def __init__(self, img_paths, arr_path, img_dims=None):
        # Load and setup assets.
        self.images = self.load_images(img_paths, img_dims)
        self.height, self.width = self.images.shape[1:]
        self.arr_path = arr_path
        self.ink_map = np.zeros((self.height, self.width))
        
        # Setup defaults.
        self.cell_size = 9
        self.grid_iter = (20, 5) # (y_step, x_step)
        self.cell_iter = (2, 4, 2, 4) # (y_start, y_step, x_start, x_step)
        self.num_cell_checks = 4

    def cell_settings(self, cell_size, cell_iter):
        self.cell_size = cell_size
        self.cell_iter = cell_iter
        self.num_cell_checks = (((cell_size - cell_iter[0])//cell_iter[1])+1) * (((cell_size - cell_iter[2])//cell_iter[3])+1)

    def grid_settings(self, grid_iter):
        self.grid_iter = grid_iter

    def load_images(self, paths, dims=None):
        if dims:
            images = [(np.array(Image.open(path), dtype=np.float32)/65535.0)[dims[0]:dims[1], dims[2]:dims[3]] for path in paths]
        else:
            images = [np.array(Image.open(path), dtype=np.float32)/65535.0 for path in paths]
        images = np.array(images).astype('float32')
        return images

    def initialise_grid(self, dims):
        grid = np.full((self.grid_y, self.grid_x), False)
        for (y, x), element in np.ndenumerate(grid):
            if self.images[0, dims[0]+65+(y*self.cell_size), dims[2]+65+(x*self.cell_size)] != 0:
                grid[y, x] = True
        return grid

    def find_ink(self, dims, model, threshold, method='avg', verbose=True):
        self.threshold = threshold
        self.grid_y = ((dims[1]-65) - (dims[0]+65))//self.cell_size
        self.grid_x = ((dims[3]-65) - (dims[2]+65))//self.cell_size
        self.grid = self.initialise_grid(dims)
        
        num_pixels = np.count_nonzero(self.grid)
        print(f'Number of Pixel Clusters: {num_pixels}')
        
        # Iterate through every twentieth y-sections and fifth x-sections.
        ps = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
        percent_previous = -1.0
        for (y, x), element in np.ndenumerate(self.grid):
            percent = ((y*self.grid_x + x + 1) / (self.grid_y*self.grid_x)) * 100
            if element == True and y % self.grid_iter[0] == 0 and x % self.grid_iter[1] == 0 and self.ink_map[dims[0]+65+(y*self.cell_size), dims[2]+65+(x*self.cell_size)] == 0:
                self.check_cells(dims, model, method, start=(y, x))
            
            if percent >= ps[-1]:
                save_slice = dims[0]+65+(y*self.cell_size)
                self.save_array()
                ps.pop()
            
            if verbose and percent >= percent_previous + 0.1:
                percent_previous = percent
                print(f'Percent Complete: {percent:.1f} %  Current Save Slice: {save_slice}', end='\r')
        print(f'Percent Complete: {percent:.1f} %  Current Save Slice: {save_slice}')
        self.save_array()

    def check_cells(self, dims, model, method, start):
        cells_to_check = deque([start])
        while cells_to_check:
            current = cells_to_check.popleft()
            cell_value = self.find_cell_value(dims[0]+65+(current[0]*self.cell_size), dims[2]+65+(current[1]*self.cell_size), model, method, self.images)
            self.ink_map = sf.grid_update(self.ink_map, dims[0]+65+(current[0]*self.cell_size), dims[2]+65+(current[1]*self.cell_size), cell_value, self.cell_size)
            self.grid[current[0], current[1]] = False
            if cell_value >= self.threshold:
                cells_to_check = self.fetch_neighbours(current, cells_to_check)

    def fetch_neighbours(self, current, cells_to_check):
        if current[0] > 0 and self.grid[current[0]-1, current[1]] == True and (current[0]-1, current[1]) not in cells_to_check:
            cells_to_check.append((current[0]-1, current[1]))
        if current[0] < self.grid.shape[0]-1 and self.grid[current[0]+1, current[1]] == True and (current[0]+1, current[1]) not in cells_to_check:
            cells_to_check.append((current[0]+1, current[1]))
        if current[1] > 0 and self.grid[current[0], current[1]-1] == True and (current[0], current[1]-1) not in cells_to_check:
            cells_to_check.append((current[0], current[1]-1))
        if current[1] < self.grid.shape[1]-1 and self.grid[current[0], current[1]+1] == True and (current[0], current[1]+1) not in cells_to_check:
            cells_to_check.append((current[0], current[1]+1))
        return cells_to_check

    def save_array(self):
        np.save(self.arr_path, self.ink_map)

    def save_image(self, filepath):
        ink_img = Image.fromarray(((self.ink_map/self.ink_map.max())*255).astype('uint8'))
        ink_img.save(filepath)

    def find_cell_value(self, i, j, model, method, images):
        arrays = np.empty((self.num_cell_checks, 8, 65, 65), dtype='float32')
        count = 0
        for grid_y in range(self.cell_iter[0], self.cell_size, self.cell_iter[1]):
            for grid_x in range(self.cell_iter[2], self.cell_size, self.cell_iter[3]):
                arrays[count] = sf.create_sub_volume(j+grid_x, i+grid_y, images)
                count += 1
        predictions = model(arrays, training=False)
        if method == 'max':
            return np.max(predictions)
        else:
            return np.mean(predictions)
