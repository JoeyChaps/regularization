#!/usr/bin/python
#######
# File: Regularizer.py
# Project: Regularization
# Author: Joe Chapman
# Date: 9-8-14
# Url: https://github.com/JoeyChaps/regularization
#######
import math
import numpy as np
from numpy.linalg import inv
import os
from reportlab.pdfgen import canvas as pdffile
import Transforms
import GraphPlot


class Regularizer:
    """A class that mitigates overfitting in multivariant linear regression 
    using regularization through weight decay. 
    """

    def __init__(self, outputPath):
        self.pdfString = ""
        self.outputPath = outputPath
        self.directory = "output"
        self.regularPatterns = []

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.wFileName = outputPath + "\\results.txt"
        self.pdfFileName = outputPath + "\\results.pdf"
        self.patternPlot = GraphPlot.GraphPlotter(
            outputPath + "\\patterns.png", "Average Intensity", "Symmetry", 
            "Digit Recognition", "toprightout")


    def runAlgorithm(self, classIndex, xIndex, yIndex, ncolumns, transNumber, 
                     nTrainPats, a_Lambdas, a_TrainPatterns, dataFunction):
        """Runs the program, storing the results table in a PDF file and the 
        graph in a PNG file.
        """

        a_ww = []
        a_desiredYns = []
        a_pats = list(a_TrainPatterns)
        a_desiredYns = self.plotRegularizations(xIndex, yIndex, a_pats)

        for a_row in a_pats:
            del a_row[classIndex]

        t_form = Transforms.Transform(transNumber, 0)
        sTransVers = t_form.getTransformVersion()

        if (sTransVers):
            transform = t_form.getTransform()
            a_transPats = transform(a_pats)
            a_pats = []
            a_pats = list(a_transPats)    

        ncolumns = len(a_pats[0])
        a_Eaug = []

        for lam in a_Lambdas:
            print("\ntraining with lambda - " + str(lam) + " ...\n")

            trainEin, a_ww = self.trainWeights(ncolumns, nTrainPats, lam,  
                a_desiredYns, a_pats)

            Eaug, LWregTWreg = self.getEaug(lam, trainEin, a_ww)
            a_Eaug.append([lam, trainEin, LWregTWreg, Eaug])
            self.plotClassifiers(a_ww, dataFunction, lam)

        self.buildRegularizationResultsTable(a_Eaug)        
        self.writePdf(self.pdfFileName)


    def plotRegularizations(self, xIn, yIn, a_patterns):
        """Loads the regularPatterns list of x values and y values and returns 
        the list of y values.
        """

        a_X = []
        a_Y = []
        a_pats = list(a_patterns)

        for a_row in a_pats:
            a_X.append(a_row[xIn])
            a_Y.append(a_row[yIn])

        self.regularPatterns = [a_X, a_Y]

        return list(a_Y)


    def plotClassifiers(self, a_wts, dataFunc, lam):
        """Graphs the data function and decay function."""

        xMin = math.floor(self.patternPlot.getXMin())
        xMax = math.ceil(self.patternPlot.getXMax())
        xMin = -1.5
        xMax = 1.5
        xRange = np.linspace(xMin, xMax * 1, num=200)
        
        decayFunc = lambda x: (a_wts[0] * x) + \
                               (a_wts[1] * x**2) + \
                               (a_wts[2] * x**3) + \
                               (a_wts[3] * x**4) + \
                               (a_wts[4] * x**5)

        a_xstar = []
        a_xbase = []
        a_graphData = []

        for x1 in xRange:                               
            xstar = decayFunc(x1)
            a_xstar.append(xstar)
            xbase = dataFunc(x1)
            a_xbase.append(xbase)        

        a_graphData.append([xRange, a_xstar, 'c-', "$\lambda$ = " + str(lam)])
        a_graphData.append([xRange, a_xbase, 'r-', "$f$($x$) = 1 + 9$x^2$"])
        self.saveDecayGraph(lam, a_graphData)
        

    def saveDecayGraph(self, lamb, a_graphInfo):
        """Saves the graph."""

        graphFile = self.outputPath + "\\decayGraph-Lambda_" + str(lamb) + ".png"
        decayPlot = GraphPlot.GraphPlotter(graphFile, "X", "Y", "Weight Decay", "toprightout")

        for info in a_graphInfo:
            decayPlot.addGraph(info[0], info[1], info[2], info[3])

        a_X = self.regularPatterns[0]
        a_Y = self.regularPatterns[1]

        decayPlot.addGraph(a_X, a_Y, 'bs', 'patterns')

        a_dims = [-1.5, 1.5, -10, 20]
        decayPlot.plotGraphs(a_dims)


    def trainWeights(self, ncols, npats, lamb, a_desiredYns, a_pats):
        """Trains a set of weights for the data in the a_pats list using
        pseudo-inversion regularized by a lambda factor and returns the 
        in-sample error and list of weights.
        """

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

        return [Ein, list(a_ww)]


    def getYFit(self, ncols, a_x, a_w):
        """Returns the sum of inputs times their weights."""

        y = 0

        for c in range(0, ncols):
            y += a_x[c] * a_w[c]

        return y


    def getInErr(self, npatterns, a_desYn, a_actYn):
        """Returns the error as the average squared difference between actual
        output and desired output.
        """

        errSum = 0
        
        for p in range(0, npatterns):
            errSum += ((a_actYn[p] - a_desYn[p]) * (a_actYn[p] - a_desYn[p]))

        return float(errSum) / npatterns


    def getEaug(self, lamb, ein, a_wts):
        """Returns augmented error and its component: the product of lambda 
        times the transpose of the regularized weight vector times the 
        regularized weight vector.
        """

        EinWreg = ein
        np_wts = np.array(a_wts)
        np_WregT = np_wts.transpose()
        np_LWregT = lamb * np_WregT
        np_LWregTWreg = np.dot(np_LWregT, np_wts)
        Eaug = EinWreg + np_LWregTWreg

        return Eaug, np_LWregTWreg


    def buildRegularizationResultsTable(self, a_Eaug):
        """Builds a table of in-sample error and augmented error for each 
        lambda value.
        """

        self.addToPdfString(
            "  lambda  |   Ein(Wreg)  | lambda*WregT*Wreg |   Eaug    \n")

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
        """Returns a string of a number centered in a table cell row."""

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
        """Returns a string for a blank table cell row."""

        sBlank = ""
        sLen = len(sBlank)

        while (sLen < len(sLine)):
            sBlank = sBlank + " "
            sLen = len(sBlank)

        return sBlank


    def insertNum(self, sNum, ch):
        """Returns a string of a number with the correct spacing for centering."""

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


    def addToPdfString(self, s):
        """Adds a string to content for a PDF file."""

        self.pdfString = self.pdfString + s


    def writePdf(self, fileName):
        """Saves PDF content to a file."""

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
