"""
A basic script to download a local set of data
for a specific segment from the vesuvius scroll
server. The format of the local organisation is
important for future processing.
"""

import os
import time
import requests
from requests.auth import HTTPBasicAuth

access = {'user':'####', 'pass':'####'}


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def fetch_and_save(path, url, access):
    r = requests.get(url, auth=HTTPBasicAuth(access['user'], access['pass']))
    with open(path_to_save, 'wb') as f:
        f.write(r.content)
    r = None
    time.sleep(10)


segment_num = '20231005123336'
server_path = 'http://dl.ash2txt.org/full-scrolls/Scroll1.volpkg/paths'

# Create directory.
cwd = os.getcwd()
main_dir = os.path.join(cwd, segment_num)
create_dir(main_dir)

# Create sub-directories.
stack_dir = os.path.join(main_dir, 'stack')
create_dir(stack_dir)
images_dir = os.path.join(main_dir, 'images')
create_dir(images_dir)
info_dir = os.path.join(main_dir, 'info')
create_dir(info_dir)
depth_dir = os.path.join(info_dir, 'depth_scans')
create_dir(depth_dir)

# Add data to info sub-directory.
path_to_save = os.path.join(info_dir, 'info.txt')
url = f'{server_path}/{segment_num}/author.txt'
name = requests.get(url, auth=HTTPBasicAuth(access['user'], access['pass']))
url = f'{server_path}/{segment_num}/area_cm2.txt'
area = requests.get(url, auth=HTTPBasicAuth(access['user'], access['pass']))
url = f'{server_path}/{segment_num}/meta.json'
meta = requests.get(url, auth=HTTPBasicAuth(access['user'], access['pass']))
with open(path_to_save, 'wb') as f:
    f.write(name.content)
    f.write(area.content)
    f.write(meta.content)

extensions = ['.mtl', '.obj', '.tif', '_cellmap.tif', '_mask.png']
for ex in extensions:
    path_to_save = os.path.join(info_dir, f'{segment_num}{ex}')
    url = f'{server_path}/{segment_num}/{segment_num}{ex}'
    fetch_and_save(path_to_save, url, access)

# Add data to stack sub-directory.
for i in range(25, 41):
    print(i)
    path_to_save = os.path.join(stack_dir, f'{i:02}.tif')
    url = f'{server_path}/{segment_num}/layers/{i:02}.tif'
    r = requests.get(url, auth=HTTPBasicAuth(access['user'], access['pass']))
 
    with open(path_to_save, 'wb') as f:
        f.write(r.content)
    r = None
    time.sleep(20)

