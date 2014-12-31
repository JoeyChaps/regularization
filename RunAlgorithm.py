#!/usr/bin/python
#######
# File: RunAlgorithm.py
# Project: Regularization
# Author: Joe Chapman
# Date: 9-8-14
# Url: https://github.com/JoeyChaps/regularization
#######
import Regularizer
import DataRandomizer
from time import gmtime, strftime
import os
import math
import shutil
import sys
import getopt


def isnumber(s):
    # Returns true if s is numeric
    bResult = True
    try: 
        i = float(s)
    except ValueError, TypeError:
        bResult = False

    return bResult


def loadData(dataFile):
    # Reads the csv dataFile and returns a 2d list of pattern data
    readFile = open(dataFile, 'r') 

    count = 0
    prev = 0
    cols = 0
    a_pats = []

    bDeleteColumn = False

    a_deleteCols = []

    for line in readFile:
        prev = cols

        a_rowp = []
        a_rowp = line.split(",")    
        a_rown = []    

        cols = len(a_rowp)

        for c in range(0, cols):
            if isnumber(a_rowp[c]): 
                a_rown.append(a_rowp[c])
            else:
                if not c in a_deleteCols:
                    a_deleteCols.append(c)

        cols = len(a_rown)

        if (cols != prev):
            if (count != 0):
                print("unequal line counts: " + str(cols) + " and " + str(prev) \
                      + " at line " + str(count) + "\n")

        count += 1

        a_pats.append(a_rown)

    for c in a_deleteCols:
        print("in load data, deleted column " + str(c))

    readFile.close()

    return list(a_pats)


def convertClasses(a_pattern, index, targetVal):
    # Replaces class values not equal to the targetVal with -1
    a_pat = list(a_pattern)

    if (a_pat[index] != targetVal):
        a_pat[index] = -1

    return list(a_pat)


def prepPats(a_pats, clsIndx, cols, bConvert):
    # Makes sure pattern values are floats and, if bConvert is true, 
    # converts class values to 1 and -1
    
    a_tmp = []

    for a_pat in a_pats:
        for c in range(0, cols + 1):
            a_pat[c] = float(a_pat[c])
        if (bConvert):
            a_pat = convertClasses(a_pat, clsIndx, 1)
        a_tmp.append(a_pat)

    return list(a_tmp)


def prepLambdas(sLambdas):
    # Makes sure lambda values are floats
    a_tmp = []

    a_lams = sLambdas.split(",")

    for lam in a_lams:
        a_tmp.append(float(lam))

    return list(a_tmp)


def main(argv):

    patsLim = -1    # This number determines how many patterns will be used in 
                    # this run of the program. The number is the total number 
                    # of train and test patterns combined. Or set patsLim to -1
                    # to use all the available patterns in the original data 
                    # set (the file referenced by the fileName variable below), 
                    # however many there may be.  
    
    bRefreshData = True     # When bRefreshData is true, the program generates 
                            # new data files for the training and test sets, 
                            # randomly selecting and ordering the data for the 
                            # new program run. When bRefreshData is false, the 
                            # program uses previously generated data files 
                            # stored in the saved_data directory.

    a_lambdas = "0"
    projectName = "regularize"
    fileName = ""
    savedDataDir = "saved_data"
    savedTrainingFile = "\\regularize_train.csv"
    rTrainFileName = "" 
    dataSource = ""
    a_trainPats = []
    nTrainPats = 0
    bConvertClass = False
    ncols = -1
    classIndex = 1
    xIn = 0
    yIn = 1
    transNum = 3
    dataFunc = lambda x: 1 + 9 * x**2

    opt = []
    arg = []

    try:
        opts, args = getopt.getopt(argv, "l:p:d", ["lambdas=", "pats=", "data"])
            
    except getopt.GetoptError as err:
        print("blarf")
        print(str(err))
        sys.exit(2)

    for opt, arg in opts:

        if opt in ("-p", "--pats"):

            patsLim = int(arg)

        elif opt in ("-d", "--data"):
            
            bRefreshData = False

        elif opt in ("-l", "--lambdas"):

            a_lambdas = arg
            transNum = 3

    nowTime = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
    newOutputDir = "" 
    otherFileName = ""

    if patsLim < 2:
        patsLim = 5
        
    a_lambdas = prepLambdas(a_lambdas)

    if bRefreshData:
        data_randomizer = DataRandomizer.DataRandomizer(
            fileName, projectName, patsLim)

        data_randomizer.generateData(patsLim, dataFunc)        
        rTrainFileName = data_randomizer.getTrainFile()
        dataSource = data_randomizer.getDataDirectory()
    else:
        rTrainFileName = savedDataDir + savedTrainingFile

    a_trainPats = loadData(rTrainFileName)
    ncols = len(a_trainPats[0]) - 1    
    a_trainPats = prepPats(a_trainPats, classIndex, ncols, bConvertClass)
    nTrainPats = len(a_trainPats)
    newOutputDir = "output\\out_" + nowTime + "_" + str(nTrainPats)

    if not os.path.exists(newOutputDir):
        os.makedirs(newOutputDir)

    if bRefreshData:
        shutil.move(dataSource, newOutputDir)
    else:
        dataDir = newOutputDir + "\\data"

        if not os.path.exists(dataDir):
            os.makedirs(dataDir)

        shutil.copy(rTrainFileName, dataDir)

        if otherFileName:
            shutil.copy(otherFileName, dataDir)

    reg = Regularizer.Regularizer(newOutputDir)
    reg.runAlgorithm(classIndex, xIn, yIn, ncols, transNum, nTrainPats, 
                     a_lambdas, a_trainPats, dataFunc)
        
    print("\nDone!")


if __name__ == "__main__":
    main(sys.argv[1:])
