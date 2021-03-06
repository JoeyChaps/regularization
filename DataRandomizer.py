#!/usr/bin/python
#######
# File: DataRandomizer.py
# Project: Regularization
# Author: Joe Chapman
# Date: 9-8-14
# Url: https://github.com/JoeyChaps/regularization
#######
import os
import random
from time import gmtime, strftime
import calendar
import numpy as np


class DataRandomizer:
    """A class that reads a data file, randomly orders the patterns, and 
    creates files for the training, test, and validation sets as called for.
    """

    def __init__(self, fileName, projectName, patsLim):
        self.npatterns = 0
        self.ncolumns = 0
        self.project = projectName
        self.dataFile = fileName
        self.patsLimit = patsLim
        self.totalPatterns = 0

        self.directory = "data"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.trainFile = self.directory + "\\" + projectName + "_train.csv"
        self.testFile = self.directory + "\\" + projectName + "_test.csv"
        self.valFile = self.directory + "\\" + projectName + "_val.csv"

        
    def getTrainFile(self):
        """Returns the name of the training set file."""

        return self.trainFile

    def getTestFile(self):
        """Returns the name of the test set file."""

        return self.testFile

    def getValFile(self):
        """Returns the name of the validation set file."""

        return self.valFile

    def getDataDirectory(self):
        """Returns the directory containing the new data files."""

        return self.directory

    def createDataFiles(self):
        """Reads the data file and creates training and test set files."""

        a_patterns = self.readDataFile()
        self.randomizeAndWriteTrainAndTest(a_patterns)
        
    def createTrainFile(self):
        """Reads the data file and creates a training set file."""

        a_patterns = self.readDataFile()
        self.randomizeAndWriteTrain(a_patterns)
        
    def createTrainAndValFiles(self):
        """Reads the data file and creates training and validation set files."""

        a_patterns = self.readDataFile()
        self.randomizeAndWriteTrainAndVal(a_patterns)
    
    def generateData(self, patsLimit, func):
        """Creates a data file of random values."""

        a_patterns = []
        npats = patsLimit
        mean = 0
        variance = 1

        seed = calendar.timegm(gmtime())
        random.seed(seed)

        for p in range(0, npats):
            noise = np.random.normal(mean, variance, 1)
            x = (float(random.randrange(-1000, 1000)) / 1000)
            y = func(x) + noise

            a_patterns.append([x,y[0]])

        self.writeNewDataFile(a_patterns)
        

    def writeNewDataFile(self, a_patterns):
        """Writes a training set file from a set of pattern values."""

        writeTrainFile = open(self.trainFile, 'w')

        a_pats = list(a_patterns)
        
        for a_pat in a_pats:

            s = str(a_pat[0])

            for p in range(1, len(a_pat)):                
                s = s + "," + str(a_pat[p])

            s = s + "\n"

            writeTrainFile.write(s)

        writeTrainFile.close() 


    def readDataFile(self):
        """Reads the class objects's dataFile and returns a list of patterns."""

        readFile = open(self.dataFile, 'r')

        count = 0
        prev = 0
        cols = 0
        a_pats = []

        for line in readFile:
            prev = cols

            a_rowp = []
            a_rowp = line.split(",")

            cols = len(a_rowp)

            if (cols != prev):
                if (count != 0):
                    
                    print("unequal line counts: " + str(cols) + " and " + \
                          str(prev) + " at line " + str(count) + "\n")

            count += 1

            a_pats.append(a_rowp)

        readFile.close()

        self.totalPatterns = len(a_pats)

        if (self.patsLimit > 0):
            self.npatterns = self.patsLimit
        else:
            self.npatterns = len(a_pats)

        self.ncolumns = cols

        readFile.close()

        print("number of patterns: " + str(len(a_pats)) + "\n")

        return list(a_pats)


    def randomizeAndWriteTrain(self, a_pats):
        """Arranges the patterns in a random order, and writes them to a 
        training set file.
        """

        writeTrainFile = open(self.trainFile, 'w')

        npats = self.npatterns # + 1
        ncols = self.ncolumns
        tpats = self.totalPatterns

        count = 0

        x = calendar.timegm(gmtime())
        random.seed(x)

        while (npats > 1):
            index = 0

            index = random.randrange(1, tpats)

            s = a_pats[index][0]

            for i in range(1, ncols):
                s = s  + "," + a_pats[index][i]

            writeTrainFile.write(s)

            del a_pats[index]

            tpats -= 1
            npats -= 1
            count += 1

        writeTrainFile.close() 


    def randomizeAndWriteTrainAndTest(self, a_pats):
        """Arranges the patterns in a random order, and writes them to 
        training and test set files.
        """

        writeTestFile = open(self.testFile, 'w')
        writeTrainFile = open(self.trainFile, 'w')

        npats = self.npatterns
        ncols = self.ncolumns
        tpats = self.totalPatterns

        partition = npats * .1

        x = calendar.timegm(gmtime())
        random.seed(x)

        # first create the training set
        while (npats > partition):

            index = random.randrange(1, tpats )

            s = a_pats[index][0]

            for i in range(1, ncols):
                s = s  + "," + a_pats[index][i]

            writeTrainFile.write(s)

            del a_pats[index]

            tpats -= 1
            npats -= 1

        # then create the test set
        while (npats > 1):

            index = random.randrange(1, tpats )

            s = a_pats[index][0]

            for i in range(1, ncols):
                s = s  + "," + a_pats[index][i]

            writeTestFile.write(s)

            del a_pats[index]

            tpats -= 1
            npats -= 1

        writeTestFile.write(s)

        writeTestFile.close() 
        writeTrainFile.close() 


    def randomizeAndWriteTrainAndVal(self, a_pats):
        """Arranges the patterns in a random order, and writes them to 
        training and test set files.
        """

        writeValFile = open(self.valFile, 'w')
        writeTrainFile = open(self.trainFile, 'w')

        npats = len(a_pats)

        nval = self.patsLimit

        if (nval < 0):
            nval = .1 * npats

        ncols = self.ncolumns
        tpats = self.totalPatterns

        partition = nval

        x = calendar.timegm(gmtime())
        random.seed(x)

        while (npats > partition):

            index = random.randrange(1, tpats )

            s = a_pats[index][0]

            for i in range(1, ncols):
                s = s  + "," + a_pats[index][i]

            writeTrainFile.write(s)

            del a_pats[index]

            tpats -= 1
            npats -= 1
        
        while (npats > 1):

            index = random.randrange(1, tpats )

            s = a_pats[index][0]

            for i in range(1, ncols):
                s = s  + "," + a_pats[index][i]

            del a_pats[index]

            tpats -= 1
            npats -= 1

            writeTrainFile.write(s)
            writeValFile.write(s)

        writeValFile.close() 
        writeTrainFile.close() 



