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
import time
from time import gmtime, strftime
import os
import math
import shutil
import numpy as np
import sys
import getopt


def printAndWrite(wFile, s):
    wFile.write(s)
    print(s)


def isnumber(s):
    
    bResult = True
    try: 
        i = float(s)
    except ValueError, TypeError:
        bResult = False

    return bResult


def loadData(dataFile):

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
            if isnumber(a_rowp[c]): # or (bDeleteColumn):
                a_rown.append(a_rowp[c])
            else:
                if not c in a_deleteCols:
                    a_deleteCols.append(c)
                # bDeleteColumn = True

        cols = len(a_rown)

        if (cols != prev):
            if (count != 0):
                print("unequal line counts: " + str(cols) + " and " + str(prev) + " at line " + str(count) + "\n")

        count += 1

        a_pats.append(a_rown)

    for c in a_deleteCols:
        print("in load data, deleted column " + str(c))

    readFile.close()

    return list(a_pats)


def convertClasses(a_pattern, index, targetVal):

    a_pat = list(a_pattern)

    if (a_pat[index] != targetVal):
        a_pat[index] = -1

    return list(a_pat)


def prepPats(a_pats, clsIndx, cols, bConvert):
    a_tmp = []

    for a_pat in a_pats:
        for c in range(0, cols + 1):
            a_pat[c] = float(a_pat[c])
        if (bConvert):
            a_pat = convertClasses(a_pat, clsIndx, 1)
        a_tmp.append(a_pat)

    return list(a_tmp)


def prepLambdas(sLambdas):
    a_tmp = []

    a_lams = sLambdas.split(",")

    for lam in a_lams:
        a_tmp.append(float(lam))

    return list(a_tmp)


def main(argv):

    patsLim = -1    # This number determines how many patterns will be used in this run of
                    # the program. The number is the total number of train and test patterns
                    # combined. Or set patsLim to -1 to use all the available patterns in the 
                    # original data set (the file referenced by the fileName variable below), 
                    # however many there may be.  
    
    bRefreshData = True     # When bRefreshData is true, the program generates new data files
                            # for the training and test sets, randomly selecting and ordering 
                            # the data for the new program run. When bRefreshData is false,
                            # the program uses previously generated data files stored in the 
                            # saved_data directory.

    nMaxFeatures = 5    # Sets the number of features used in the transform. If 3, the complete 
                        # first-order transform of three features is applied. If six, the complete 
                        # second-order transform is applied. 

    bGenerateData = False     # If true, instead of reading data files, data is produced 
                            # using local generateData() method.

    sMode = "Train"

    a_lambdas = "0"

    bRandomize = True

    projectName = "regularize"
    fileName = "one-not-one.txt"
    # fileName = "one-five-train.csv"
    savedDataDir = "saved_data"
    rTrainFileName = ""
    rValFileName = ""    
    rTestFileName = ""
    dataSource = ""
    classIndex = -1
    a_trainPats = []
    a_valPats = []
    a_testPats = []
    nTestPats = 0
    nTrainPats = 0
    nValPats = 0
    bConvertClass = False
    ncols = -1
    npats = 0
    xIn = -1
    yIn = -1
    transNum = 3
    dataFunc = lambda x: 1 + 9 * x * x

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

        elif opt in ("-f", "--features"):

            nMaxFeatures = int(arg)

        elif opt in ("-m", "--mode"):

            if ((arg == "Train") or (arg == "TrainAndTest") or (arg == "TrainAndVal")):
                sMode = arg

        elif opt in ("-d", "--data"):
            
            bRefreshData = False

        elif opt in ("-r", "--randomize"):

            bRandomize = True
            sMode = "Train"
            projectName = "regularize"

        elif opt in ("-l", "--lambdas"):

            a_lambdas = arg
            transNum = 3
            nMaxFeatures = 5
    
    if (projectName == "one-not-one"):
        bConvertClass = True

    nowTime = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
    newOutputDir = "" 
    otherFileName = ""

    if sMode == "TrainAndTest":
        if bRefreshData:
            data_randomizer = DataRandomizer.DataRandomizer(fileName, projectName, patsLim)
            data_randomizer.createDataFiles()

            rTestFileName = data_randomizer.getTestFile()
            rTrainFileName = data_randomizer.getTrainFile()

            dataSource = data_randomizer.getDataDirectory()
        else:
            rTestFileName = savedDataDir + "\\one-not-one_test.csv"
            rTrainFileName = savedDataDir + "\\one-not-one_train.csv"
            otherFileName = rTestFileName

        a_trainPats = loadData(rTrainFileName)
        nTrainPats = len(a_trainPats)
        
        a_testPats = loadData(rTestFileName)
        nTestPats = len(a_testPats)

        ncols = len(a_trainPats[0]) - 1

        if ((fileName == "one-not-one.txt") or (fileName == "one-five-train.csv")):
            classIndex = 0
            xIn = 1
            yIn = 2
        elif (fileName == "shortened_glassdata.csv"):
            classIndex = ncols

        a_trainPats = prepPats(a_trainPats, classIndex, ncols, bConvertClass)
        a_testPats = prepPats(a_testPats, classIndex, ncols, bConvertClass)        

        npats = nTrainPats + nTestPats

        newOutputDir = "output\\out_" + nowTime + "_" + str(npats) + "TrTe-" + str(nMaxFeatures)

    elif sMode == "TrainAndVal":
        if bRefreshData:
            data_randomizer = DataRandomizer.DataRandomizer(fileName, projectName, patsLim)
            data_randomizer.createTrainAndValFiles()

            rValFileName = data_randomizer.getValFile()
            rTrainFileName = data_randomizer.getTrainFile()

            dataSource = data_randomizer.getDataDirectory()
        else:
            rValFileName = savedDataDir + "\\one-not-one_val.csv"
            rTrainFileName = savedDataDir + "\\one-not-one_train.csv"
            otherFileName = rValFileName

        a_trainPats = loadData(rTrainFileName)
        nTrainPats = len(a_trainPats)

        a_valPats = loadData(rValFileName)
        nValPats = len(a_valPats)

        ncols = len(a_trainPats[0]) - 1

        if ((fileName == "one-not-one.txt") or (fileName == "one-five-train.csv")):
            classIndex = 0
            xIn = 1
            yIn = 2
        elif (fileName == "shortened_glassdata.csv"):
            classIndex = ncols

        a_trainPats = prepPats(a_trainPats, classIndex, ncols, bConvertClass)
        a_valPats = prepPats(a_valPats, classIndex, ncols, bConvertClass)    

        npats = nTrainPats + nValPats

        newOutputDir = "output\\out_" + nowTime + "_" + str(npats) + "TrVal-" + str(nMaxFeatures)

    elif sMode == "Train":

        savedTrainingFile = "\\one-not-one_train.csv"

        if bRandomize:
            if patsLim < 2:
                patsLim = 5
                
            a_lambdas = prepLambdas(a_lambdas)
            savedTrainingFile = "\\regularize_train.csv"

        if bRefreshData:
            data_randomizer = DataRandomizer.DataRandomizer(fileName, projectName, patsLim)

            if bRandomize:
                data_randomizer.generateData(patsLim, dataFunc)
            else:            
                data_randomizer.createTrainFile()
            
            rTrainFileName = data_randomizer.getTrainFile()
            dataSource = data_randomizer.getDataDirectory()
        else:
            rTrainFileName = savedDataDir + savedTrainingFile

        a_trainPats = loadData(rTrainFileName)

        ncols = len(a_trainPats[0]) - 1

        if bRandomize:
            classIndex = 1
            bConvertClass = False
            xIn = 0
            yIn = 1
        elif ((fileName == "one-not-one.txt") or (fileName == "one-five-train.csv")):
            classIndex = 0
            xIn = 1
            yIn = 2
        elif (fileName == "shortened_glassdata.csv"):
            classIndex = ncols
        
        a_trainPats = prepPats(a_trainPats, classIndex, ncols, bConvertClass)

        nTrainPats = len(a_trainPats)
        npats = nTrainPats

        newOutputDir = "output\\out_" + nowTime + "_" + str(npats)

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

    reg = Regularizer.Regularizer(newOutputDir, transNum, projectName)

    if sMode == "Train":
        reg.runAlgorithm(nMaxFeatures, classIndex, xIn, yIn, ncols, a_lambdas, nTrainPats, 0, [], a_trainPats, dataFunc)
    elif sMode == "TrainAndTest":
        reg.runAlgorithm(nMaxFeatures, classIndex, xIn, yIn, ncols, a_lambdas, nTrainPats, nTestPats, a_testPats, a_trainPats, dataFunc)
    elif sMode == "TrainAndVal":
        reg.runAlgorithm(nMaxFeatures, classIndex, xIn, yIn, ncols, a_lambdas, nTrainPats, nValPats, a_valPats, a_trainPats, dataFunc)
        
    print("\nDone!")


if __name__ == "__main__":
    main(sys.argv[1:])
