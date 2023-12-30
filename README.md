# segment_ink_detection
A pipeline to load and process scroll segments for ink detection.

This pipeline has the following dependencies (most are included with python):  
Python 3 and Jupyter Notebooks with libraries:  
1. requests
2. Pillow (PIL.Image)
3. numpy
4. statistics
5. matplotlib
6. random
7. collections (deque)
8. time
9. os
10. tensorflow 2.13.0

I find that the WinPython small setup very useful (https://winpython.github.io/).

In order to process a segment you must first load the segment using the import_segment.py script. This needs to be opened and the authentication details edited to allow downloads from the server. You can also select which segment you wish to download and how many slices to include in the stack (I usually only take 25-40).

Once the segment is loaded, it is first processed with a depth scan (01_Depth_Scan) to find a good range of slices to use in the ink detection process. Run the depth scan notebook and update the second code cell with the correct segment number and the range of slices you want to use in the scan e.g. r = [25, 41]. Note the final slice in the range is not included so this would only use 25 to 40. Once you have a plot of intensity against slice number you want to select a range of 8 slices that adequately cover the right hand side of the peak slope. This is often around 29-36 or 30-37. The scan is automatically saved in depth_scans within the info directory.

Now run the 02_Ink_Detection notebook and update the second code cell with your segment of interest. Run the first three cells to load your model. The fourth cell contains a number of settings which are included in the video guide. However, in brief, the steps are the first number of the range to include in the detection (I like to run at least 29-36 and 30-37 so that would be 29, 30 in the steps). The ink detector class has a lot of settings but including img_dims which can be used to load only a small part of a segment for quick analysis. The only other setting I would alter at the minute is threshold (between 0 and 1) which basically increases the sensitivity of the output where 0.1 is noisier but potentially captures weak ink signal and 0.7 is very clean but can miss weaker signals. The output of the ink detection is automatically saved in the images directory. However, for long runs I also like to check on the results using the analysis notebook.

The other two notebooks are for image processing and are discussed more in the video guide.
