Program Files: Regularizer.py, RunAlgorithm.py, DataRandomizer.py, 
				Transforms.py, and GraphPlot.py
Project: Regularization
Author: Joe Chapman
Date: 9-8-14
Url: https://github.com/JoeyChaps/regularization
Data Files: none


Description

    A program to mitigate overfitting in multivariant linear regression 
    using regularization through weight decay.


Development/Test Environment

    OS: 64-bit Windows 8 
    Python Version: 2.7.7.amd64
    Required Modules: numpy 1.8.1, matplotlib 1.3.1


Installation 
    
    - Python: Visit https://www.python.org/download/ to download Python 
    2.7. Download the correct version for your OS and system architecture. 
    Run the installer, and add the location of the installed python directory 
    to your PATH environment variable.

    - Numpy: If installing numpy in 32-bit Windows, visit 
    http://sourceforge.net/projects/numpy/files/NumPy/1.8.1/ to download 
    the latest version. Version 1.8.1 is for python version 2.7.7. But 
    if you're installing numpy in 64-bit Windows, you should instead go 
    to http://www.lfd.uci.edu/~gohlke/pythonlibs/ and download the Numpy-MKL 
    1.8 extension package for 64-bit architectures. Grab the executable 
    labeled py2.7 if using python 2.7.

    - Matplotlib: Visit http://matplotlib.org/downloads.html to get the 
    correct version of matplotlib for your environment. Grab the executable 
    labeled py2.7 if using python 2.7.


Running the Program

    To run the program from the command line, navigate to the directory 
    containing the program files. To run the program with default settings, 
    use the following command: 

        python RunAlgorithm.py

    The following command-line options are available to change the number 
    of patterns, lambda values, and data refresh mode: [-p, --pats=], 
    [-l, --lambda=], and [-d, --data]. (The defaults are to use five patterns,
    to use 0 for lambda, and to refresh the data each time, meaning the 
    DataRandomizer arranges a fresh set of patterns for the training set.) 
    The patterns option requires positive integer arguments:

        python RunAlgorithm.py -p 7
        python RunAlgorithm.py --pats=7

    The lambda option requires one or more positive rational arguments, 
    delimited by commas, and concatenated as a single string without 
    spaces or quotation marks:

        python RunAlgorithm.py -l .01,.1,0,1,10
        python RunAlgorithm.py --lambda=.01,.1,0,1,10

    The data refresh option doesn't take an argument:

        python RunAlgorithm.py -d
        python RunAlgorithm --data

    The program creates a folder called "output" in which to store results. 
    In the output folder, a time-stamped subfolder contains a decayGraph 
    png file for each lambda value, a results.pdf file, and a data folder 
    containing the coordinates of the data points in a csv file (copy this 
    file to the save_data folder and use the -d/--data option to reuse the 
    data file).





