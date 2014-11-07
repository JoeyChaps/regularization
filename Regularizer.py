#!/usr/bin/python
#######
# File: Regularizer.py
# Project: Regularization
# Author: Joe Chapman
# Date: 9-8-14
# Url: https://github.com/JoeyChaps/regularization
#######
from time import gmtime, strftime
import math
import numpy as np
from scipy import optimize
from numpy.linalg import inv
import os
import shutil
import Transforms
import GraphPlot
from reportlab.pdfgen import canvas as pdffile


class Regularizer:

    def __init__(self, outputPath, transNum, projName):
        self.npatterns = 0
        self.transNumber = transNum
        self.pdfString = ""
        self.outputPath = outputPath
        self.directory = "output"
        self.ones = 0
        self.notones = 0
        self.a_pocketAlgWts = [11, 1.200828152, 7.852]
        self.project = projName
        self.lineCount = 0
        self.regularPatterns = []

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.wFileName = outputPath + "\\results.txt"
        self.pdfFileName = outputPath + "\\results.pdf"
        self.patternPlot = GraphPlot.GraphPlotter(outputPath + "\\patterns.png", "Average Intensity", "Symmetry", "Digit Recognition", "toprightout")


    def runAlgorithm(self, nMaxFeatures, classIndex, xIndex, yIndex, ncolumns, a_Lambdas, nTrainPats, nTestPats, a_TestPatterns, a_TrainPatterns, dataFunction):

        a_ww = []
        a_desiredYns = []
                
        a_pats = list(a_TrainPatterns)

        if self.project == "regularize":
            a_desiredYns = self.plotRegularizations(xIndex, yIndex, a_pats)

        elif self.project == "one-not-one":

            a_desiredYns = self.plotOnesNotOnes(classIndex, xIndex, yIndex, a_pats)
        
        for a_row in a_pats:
            del a_row[classIndex]

        t_form = Transforms.Transform(self.transNumber, nMaxFeatures)
        t_form.setTransformCount(nMaxFeatures)

        sTransVers = t_form.getTransformVersion()

        if (sTransVers):
            transform = t_form.getTransform()
            a_transPats = transform(a_pats)
            a_pats = []
            a_pats = list(a_transPats)    

        ncolumns = len(a_pats[0])

        sTransDef = t_form.getTransformDef()

        if self.project == "regularize":

            a_Eaug = []

            for lam in a_Lambdas:
                print("\ntraining with lambda - " + str(lam) + " ...\n")

                trainEin, accuracy, a_ww = self.trainWeights(ncolumns, nTrainPats, lam, a_desiredYns, a_pats)
                Eaug, LWregTWreg = self.getEaug(lam, trainEin, a_ww)
                a_Eaug.append([lam, trainEin, LWregTWreg, Eaug])
                self.plotClassifiers(nMaxFeatures, a_ww, dataFunction, lam)

            self.buildRegularizationResultsTable(a_Eaug)

        else:
            self.addToPdfString("---------------------------------\n")
            self.addToPdfString("TRAINING WHOLE SET\n")    
            sTransform = self.printAndGetTransformInfo(sTransDef, sTransVers)            
            print("\ntraining whole set - " + sTransform + " ...\n")

            trainEin, accuracy, a_ww = self.trainWeights(ncolumns, nTrainPats, lam, a_desiredYns, a_pats)
            
            self.plotClassifiers(nMaxFeatures, a_ww, dataFunction)
            self.printAndGetTransformInfo(sTransDef, sTransVers)
            self.writeWeights(a_ww)
            self.addToPdfString("\nE-train: " + str(round(trainEin, 3)) + "\n\n")

            self.patternPlot.plotGraphs()

        if nMaxFeatures == 3:
            self.addToPdfString("---------------------------------\n")
            self.addToPdfString("TESTING POCKET ALGORITHM\n")    
            
            self.testPocketAlg(ncolumns, nTrainPats, self.a_pocketAlgWts, a_desiredYns, a_pats)

            self.addToPdfString("Weights:")

            for ww in self.a_pocketAlgWts:
                self.addToPdfString(" " + str(round(ww, 3)))

        self.writePdf(self.pdfFileName)


    def writeWeights(self, a_weights):
        self.addToPdfString("Weights:")

        for ww in a_weights:
            self.addToPdfString(" " + str(round(ww, 3)))


    def plotRegularizations(self, xIn, yIn, a_patterns):
        a_X = []
        a_Y = []

        ones = 0
        notones = 0

        a_pats = list(a_patterns)

        for a_row in a_pats:
            a_X.append(a_row[xIn])
            a_Y.append(a_row[yIn])

        self.regularPatterns = [a_X, a_Y]

        return list(a_Y)


    def plotOnesNotOnes(self, classIn, xIn, yIn, a_patterns):
        a_onesX = []
        a_onesY = []
        a_notonesX = []
        a_notonesY = []

        a_Yns = []

        ones = 0
        notones = 0

        a_pats = list(a_patterns)

        for a_row in a_pats:
            yn = a_row[classIn]
            a_Yns.append(yn)

            if (yn == 1):
                a_onesX.append(a_row[xIn])
                a_onesY.append(a_row[yIn])
            else:
                a_notonesX.append(a_row[xIn])
                a_notonesY.append(a_row[yIn])

        self.patternPlot.addGraph(a_onesX, a_onesY, 'bo', "ones")
        self.patternPlot.addGraph(a_notonesX, a_notonesY, 'rx', "not ones")

        return list(a_Yns)


    def plotClassifiers(self, nFeatures, a_wts, dataFunc, lam=-1):

        xMin = math.floor(self.patternPlot.getXMin())
        xMax = math.ceil(self.patternPlot.getXMax())

        xMin = -1.5
        xMax = 1.5

        xRange = np.linspace(xMin, xMax * 1, num=200)

        lineStyle = self.getLineStyle(self.lineCount)
        
        decayFunc = lambda x: (a_wts[0] * x) + (a_wts[1] * x * x) + (a_wts[2] * x * x * x) +\
         (a_wts[3] * x * x * x * x) + (a_wts[4] * x * x * x * x * x)

        a_xstar = []
        a_xbase = []
        a_graphData = []

        for x1 in xRange:

            if lam >= 0:                    
                xstar = decayFunc(x1)
                a_xstar.append(xstar)

                xbase = dataFunc(x1)
                a_xbase.append(xbase)        

            else:                
                if nFeatures == 3:
                    lineFunc = lambda x2: (a_wts[0]) + (a_wts[1] * x1) + (a_wts[2] * x2)    
                    xstar = optimize.fsolve(lineFunc, -1.5)
                    a_xstar.append(xstar)
                elif nFeatures == 6:
                    curveFunc = lambda x2: (a_wts[0]) + (a_wts[1] * x1) + (a_wts[2] * x2) + (a_wts[3] * x1 * x1) + \
                     (a_wts[4] * x1 * x2) + (a_wts[5] * x2 * x2)
                    xstar = optimize.fsolve(curveFunc, -1.5)
                    a_xstar.append(xstar)    

        lineStyle = self.getLineStyle(self.lineCount)
        lineStyle = 'c-'

        if lam >= 0:
            lineProp = ["$\lambda$ = " + str(lam), lineStyle]
            a_graphData.append([xRange, a_xstar, lineProp[1], lineProp[0]])
            a_graphData.append([xRange, a_xbase, 'r-', "$f$($x$) = 1 + 9$x^2$"])
            self.saveDecayGraph(lam, a_graphData)
            self.lineCount += 1
        else:
            lineProp = ["$f$($x$) = 0", lineStyle]
            self.patternPlot.addGraph(xRange, a_xstar, lineProp[1], lineProp[0])
            self.lineCount += 1

            if nFeatures == 3:    
                a_pw = self.a_pocketAlgWts
                a_xstar = []
                for x1 in xRange:
                    lineFunc = lambda x2: (a_pw[0]) + (a_pw[1] * x1) + (a_pw[2] * x2) 
                    xstar = optimize.fsolve(lineFunc, -1.5) 
                    a_xstar.append(xstar)                    

                self.patternPlot.addGraph(xRange, a_xstar, 'g-', "pocket algorithm")
                self.lineCount += 1            
        

    def saveDecayGraph(self, lamb, a_graphInfo):

        graphFile = self.outputPath + "\\decayGraph-Lambda_" + str(lamb) + ".png"
        decayPlot = GraphPlot.GraphPlotter(graphFile, "X", "Y", "Weight Decay", "toprightout")

        for info in a_graphInfo:
            decayPlot.addGraph(info[0], info[1], info[2], info[3])

        a_X = self.regularPatterns[0]
        a_Y = self.regularPatterns[1]

        decayPlot.addGraph(a_X, a_Y, 'bs', 'patterns')

        a_dims = [-1.5, 1.5, -10, 20]
        decayPlot.plotGraphs(a_dims)


    def getLineStyle(self, count):

        sLine = ''

        if count == 0:
            sLine = 'c-'
        elif count == 1:
            sLine = 'g-'
        elif count == 2:
            sLine = 'm-'
        elif count == 3:
            sLine = 'k-'
        elif count == 4:
            sLine = 'b-'
        elif count == 5:
            sLine = 'y-'
        elif count == 6:
            sLine = 'k--'
        elif count == 7:
            sLine = 'b--'
        elif count == 8:
            sLine = 'g--'

        return sLine


    def testPocketAlg(self, ncols, npats, a_wts, a_desiredYn, a_pat):

        a_actualYn = []

        for p in range(0, npats):
            for c in range(0, ncols):
                a_pat[p][c] = float(a_pat[p][c])
        
             yFit = self.getYFit(ncols, a_pat[p], a_wts)
             a_actualYn.append(yFit)
    
        Eout = self.getInErr(npats, a_desiredYn, a_actualYn)

        sMsg = "Pocket Algorithm "
        self.getAccuracy(sMsg, npats, a_desiredYn, a_actualYn)        

        return Eout


    def testWeights(self, ncols, npats, a_wts, a_desiredYn, a_pat):

        a_actualYn = []

        for p in range(0, npats):
            for c in range(0, ncols):
                a_pat[p][c] = float(a_pat[p][c])
        
             yFit = self.getYFit(ncols, a_pat[p], a_wts)
             a_actualYn.append(yFit)
    
        Eout = self.getInErr(npats, a_desiredYn, a_actualYn)

        sMsg = "Testing "
        self.testAccuracy = self.getAccuracy(sMsg, npats, a_desiredYn, a_actualYn)        

        return Eout


    def trainWeights(self, ncols, npats, lamb, a_desiredYns, a_pats):

        a_ww = []
        a_actualYn = []

        np_X = np.array(a_pats)
        np_Xt = np_X.transpose()

        np_XtX = np.dot(np_Xt, np_X)

        np_identity = np.identity(ncols)

        np_lambI = lamb * np_identity

        np_XtX_lambI = np_XtX + np_lambI
        
        np_XtXinv = inv(np_XtX_lambI)

        np_XtXinvXt = np.dot(np_XtXinv, np_Xt)
        np_Y = np.array(a_desiredYns)

        np_ww = np.dot(np_XtXinvXt, np_Y)

        a_ww = list(np_ww.tolist())

        for p in range(0, npats):
             yFit = self.getYFit(ncols, a_pats[p], a_ww)
             a_actualYn.append(yFit)

        Ein = self.getInErr(npats, a_desiredYns, a_actualYn)

        sMsg = "Training Patterns: " + str(npats) + "\nTraining "

        # accuracy = self.getAccuracy(sMsg, npats, a_desiredYns, a_actualYn)

        accuracy = 0

        return [Ein, accuracy, list(a_ww)]


    def getYFit(self, ncols, a_x, a_w):
        y = 0

        for c in range(0, ncols):
            y += a_x[c] * a_w[c]

        return y


    def getInErr(self, npatterns, a_desYn, a_actYn):
        errSum = 0
        
        for p in range(0, npatterns):
            errSum += ((a_actYn[p] - a_desYn[p]) * (a_actYn[p] - a_desYn[p]))

        return float(errSum) / npatterns


    def getAccuracy(self, sInfo, npatterns, a_desiredOuts, a_actualOuts):
        
        accuracy = 0
        a_outMat = []
        a_strMat = []
        a_desCount = []

        totalTrue = 0
        nClasses = 0

        TAB = "    "

        bPlusOneMinusOne = (-1 in a_desiredOuts)

        if bPlusOneMinusOne:
            nClasses = 2
            plusIndex = 0
            minusIndex = 1

            for r in range(0, nClasses):
                outRow = []
                strRow = []

                for c in range(0, nClasses):
                    outRow.append(0)
                    strRow.append("")

                a_outMat.append(outRow)
                a_strMat.append(strRow)
                a_desCount.append(0)

            for p in range(0, npatterns):

                dout = a_desiredOuts[p]
                aout = a_actualOuts[p]

                if (dout < 0):
                    if (aout < 0):                # true negative
                        a_outMat[minusIndex][minusIndex] += 1
                        totalTrue += 1
                    else:                        # false positive
                        a_outMat[minusIndex][plusIndex] += 1

                    a_desCount[minusIndex] += 1
                else:
                    if (aout < 0):                # false negative
                        a_outMat[plusIndex][minusIndex] += 1
                    else:                        # true positive
                        a_outMat[plusIndex][plusIndex] += 1
                        totalTrue += 1

                    a_desCount[plusIndex] += 1
        else:
            nClasses = 7

            for r in range(0, nClasses):
                outRow = []
                strRow = []

                for c in range(0, nClasses):
                    outRow.append(0)
                    strRow.append("")

                a_outMat.append(outRow)
                a_strMat.append(strRow)
                a_desCount.append(0)

            for p in range(0, npatterns):
                dout = a_desiredOuts[p]
                aout = a_actualOuts[p]

                if ((dout > 0) & (aout > dout - .5) & (aout < dout + .5)):
                    a_outMat[int(dout)][int(dout)] += 1
                    totalTrue += 1
                elif ((dout == 0) & (aout < .5)):
                    a_outMat[int(dout)][int(dout)] += 1
                    totalTrue += 1
                else:                
                    for c in range(0, nClasses):
                        if ((aout > c - .5) & (aout < c + .5)):
                            a_outMat[int(dout)][c] += 1

            a_desCount[int(dout)] += 1

            accuracy = self.getMultipleClassificationAccuracy(npatterns, a_desiredOuts, a_actualOuts)

        for r in range(0, nClasses):
            for c in range(0, nClasses):
                if (a_outMat[r][c] == 0):
                    a_strMat[r][c] = " "
                else:
                    a_strMat[r][c] = str(a_outMat[r][c])

        accuracy = float(totalTrue) / npatterns

        if bPlusOneMinusOne:
            self.buildTruthMatrix(TAB, nClasses, a_strMat, a_desCount)
        else:
            self.buildAccuracyMatrix(TAB, nClasses, a_strMat, a_desCount)

        self.addToPdfString(sInfo)
        self.addToPdfString("Accuracy: " + str(round(accuracy, 3)) + "\n")

        return accuracy


    def buildAccuracyMatrix(self, sTab, nouts, a_sOut, a_iDesCount):

        self.addToPdfString("\n" + sTab + sTab + sTab + sTab + "Expected Outputs\n")
        self.addToPdfString(sTab + sTab + sTab + sTab + " _0_  _1_  _2_  _3_  _4_  _5_  _6_\n")

        a_FramePieces = [" A      _0_   | ", "\n c O    _1_   | ", "\n t u    _2_   | ", "\n u t    _3_   | ", "\n a p    _4_   | ", "\n l u    _5_   | ", "\n   t    _6_   | "]

        for c in range(0, nouts):            
            
            self.addToPdfString(a_FramePieces[c])

            for n in range(0, nouts):
                s = ""

                if n == c:
                    s = "."

                self.addToPdfString(self.insertNum(a_sOut[n][c], s))
        
        self.addToPdfString("\n" + sTab + sTab + sTab + "  |  ___  ___  ___  ___  ___  ___  ___\n")
        self.addToPdfString(sTab + sTab + sTab + sTab)

        for c in range(0, nouts):
            self.addToPdfString(self.insertNum(str(a_iDesCount[c]), "")) 

        self.addToPdfString("\n\n")


    def buildTruthMatrix(self, sTab, nouts, a_sOut, a_iDesCount):

        self.addToPdfString("\n" + sTab + sTab + sTab + sTab + "Expected Outputs\n")
        self.addToPdfString(sTab + sTab + sTab + sTab + " _1_  -1_ \n")

        a_FramePieces = [" A      _1_   | ", "\n c O    -1_   | ", "\n t u          | ", "\n u t          | ", "\n a p          | ", "\n l u          | ", "\n   t          | "]

        nFramePieces = len(a_FramePieces)

        for c in range(0, nFramePieces):            
            
            self.addToPdfString(a_FramePieces[c])

            if c < nouts:
                for r in range(0, nouts):
                    s = ""

                    if r == c:
                        s = "."

                    self.addToPdfString(self.insertNum(a_sOut[r][c], s))
        
        self.addToPdfString("\n" + sTab + sTab + sTab + "  |  ___  ___  \n")
        self.addToPdfString(sTab + sTab + sTab + sTab)

        for c in range(0, nouts):
            self.addToPdfString(self.insertNum(str(a_iDesCount[c]), "")) 

        self.addToPdfString("\n\n")


    def getEaug(self, lamb, ein, a_wts):

        EinWreg = ein
        np_wts = np.array(a_wts)
        np_WregT = np_wts.transpose()

        np_LWregT = lamb * np_WregT
        np_LWregTWreg = np.dot(np_LWregT, np_wts)

        Eaug = EinWreg + np_LWregTWreg

        return Eaug, np_LWregTWreg


    def buildRegularizationResultsTable(self, a_Eaug):

        self.addToPdfString("  lambda  |   Ein(Wreg)  | lambda*WregT*Wreg |   Eaug    \n")

        line1 = "__________"
        line2 = "______________"
        line3 = "___________________"
        line4 = "__________"

        for Eaug in a_Eaug:

            sLam = str(Eaug[0])
            sEin = str(round(Eaug[1], 3))
            sWtW = str(round(Eaug[2], 3))
            sEaug = str(round(Eaug[3], 3))

            self.addToPdfString(
             line1 + "|" + line2 + "|" + line3 + "|" + line4 + "\n" + \
             self.insertBlankCell(line1) + "|" +\
             self.insertBlankCell(line2) + "|" +\
             self.insertBlankCell(line3) + "|" + "\n" +\
             self.insertTableNum(sLam, line1) + "|" +\
             self.insertTableNum(sEin, line2) + "|" +\
             self.insertTableNum(sWtW, line3) + "|" +\
             self.insertTableNum(sEaug, line4) + "\n" +\
             self.insertBlankCell(line1) + "|" +\
             self.insertBlankCell(line2) + "|" +\
             self.insertBlankCell(line3) + "|" + "\n")


    def insertTableNum(self, sNum, sLine):

        sLen = len(sNum)
        alt = 0

        while (sLen < len(sLine)):
            if alt:
                sNum = " " + sNum
                alt -= 1
            else:
                sNum = sNum + " "
                alt += 1

            sLen = len(sNum)

        return sNum


    def insertBlankCell(self, sLine):

        sBlank = ""
        sLen = len(sBlank)

        while (sLen < len(sLine)):
            sBlank = sBlank + " "
            sLen = len(sBlank)

        return sBlank


    def insertNum(self, sNum, ch):

        s = ""
        
        if len(sNum) == 1:

            if ch == ".":
                s = "  " + str(sNum) + ". "
            else:
                s = "  " + str(sNum) + "  "
        else:
            if len(sNum) == 2:
                s = "  " + str(sNum)

            elif len(sNum) == 3:
                s = " " + str(sNum)
            else:
                s = str(sNum)

            if ch == ".":
                s = s + "."
            else:
                s = s + " "    

        return s


    def writeToSummaryFile(self, s):
        self.summaryFile.write(s)

    def getOutputPath(self):
        return self.outputPath

    def printAndGetTransformInfo(self, transDef, transVers):
        sTrans = ""

        if (transDef):
            self.addToPdfString("Trans: " + transDef + "\n")
        else:
            self.addToPdfString("Trans: None\n")

        if (transVers):
            self.addToPdfString("Trans No.: " + transVers + "\n")
            sTrans = "transform " + transVers
        else:
            sTrans = "no transform"

        return sTrans


    def printAndGetTransformAndLambdaInfo(self, transDef, transVers, lam):
        sTrans = ""

        if (transDef):
            self.addToPdfString("Trans: " + transDef + "\n")
        else:
            self.addToPdfString("Trans: None\n")

        if (transVers):
            self.addToPdfString("Trans No.: " + transVers + "\n")
            sTrans = "transform " + transVers
        else:
            sTrans = "no transform"

        if (lam >= 0):
            self.addToPdfString("Lambda: " + str(lam) + "\n")

        return sTrans


    def addToPdfString(self, s):
        self.pdfString = self.pdfString + s

    def writePdf(self, fileName):
        title = fileName
        point = 1
        inch = 72
        canv = pdffile.Canvas(fileName, pagesize=(8.5 * inch, 11 * inch))
        canv.setStrokeColorRGB(0,0,0)
        canv.setFillColorRGB(0,0,0)
        canv.setFont("Courier", 10 * point)
            
        v = 10 * inch
        for subtline in (self.pdfString.split( '\n' )):

            endpt = 78

            if len(subtline) > endpt:

                bContinue = True

                splitStr = subtline

                while (bContinue):
                    substr = splitStr[:endpt]
                    endstr = "  " + splitStr[endpt:]

                    canv.drawString( 1 * inch, v, substr )
                    v -= 12 * point

                    if v <= 0:
                        canv.showPage()
                        v = 10 * inch
                        canv.setFont("Courier", 10 * point)

                    if (len(endstr) <= endpt):

                        canv.drawString( 1 * inch, v, endstr )
                        v -= 12 * point

                        if v <= 0:
                            canv.showPage()
                            v = 10 * inch
                            canv.setFont("Courier", 10 * point)

                        bContinue = False

                    else:
                        splitStr = endstr

            else:
                canv.drawString( 1 * inch, v, subtline )
                v -= 12 * point

                if v <= 0:
                    canv.showPage()
                    v = 10 * inch
                    canv.setFont("Courier", 10 * point)

        canv.save()
