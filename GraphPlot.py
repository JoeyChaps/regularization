#!/usr/bin/python
#######
# File: GraphPlot.py
# Project: Regularization
# Author: Joe Chapman
# Date: 9-8-14
# Url: https://github.com/JoeyChaps/regularization
#######
import matplotlib.pyplot as plt

class GraphPlotter:
    """A class that generates graphical representations of X and Y data and
    saves the graphs in a file.
    """

    def __init__(self, fileName, xText, yText, title, legend=""):

        self.sXtext = xText
        self.sYtext = yText
        self.sTitle = title
        self.a_x = []
        self.a_y = []
        self.a_types = []
        self.a_legends = []
        self.sFile = fileName
        self.xMin = 0
        self.xMax = 0
        self.yMin = 0
        self.yMax = 0
        self.graphCount = 0
        self.sLegend = legend

        if self.sTitle:    
            plt.title(self.sTitle)
        plt.ylabel(self.sYtext)
        plt.xlabel(self.sXtext)

        self.fig = plt.figure(1)
        self.ax = self.fig.add_subplot(111)


    def getXMin(self):
        """Returns the class object's value for the smallest X."""

        return self.xMin

    def getXMax(self):
        """Returns the class object's value for the largest X."""

        return self.xMax
        
    def plotGraphs(self, a_dimensions=[]):
        """Plots all of the graphs that have been added to the class object and
        saves them in a single file.

        Keyword arguments:
        a_dimensions -- the dimensions of the graph, in format [min X, max X, 
        min Y, max Y]; if a_dimensions is empty, the dimensions are set
        according to the class object's minimum and maximum X and Y values.
        """

        if self.sLegend:
            for g in range(0, self.graphCount):

                self.ax.plot(self.a_x[g], self.a_y[g], self.a_types[g], 
                             label=self.a_legends[g])

        else:            
            for g in range(0, self.graphCount):
                self.ax.plot(self.a_x[g], self.a_y[g], self.a_types[g])

        if len(a_dimensions) == 0:
            if self.xMin < 0:
                self.xMin -= (-.1 * self.xMin)

            if self.yMin < 0:
                self.yMin -= (-.1 * self.yMin)

            if self.xMax > 0:
                self.xMax += (.1 * self.xMax)

            if self.yMax > 0:
                self.yMax += (.1 * self.yMax)
        else:
            self.xMin = a_dimensions[0]
            self.xMax = a_dimensions[1]
            self.yMin = a_dimensions[2]
            self.yMax = a_dimensions[3]

        self.ax.axis([self.xMin,self.xMax,self.yMin,self.yMax])    
        handles, labels = self.ax.get_legend_handles_labels()
        
        lgd = self.ax.legend(handles, labels, loc='upper center', 
                             bbox_to_anchor=(1.18, 1.02))

        self.fig.savefig(self.sFile, bbox_extra_artists=(lgd,), 
                         bbox_inches='tight')
        
        plt.close()


    def addGraph(self, a_xAxis, a_yAxis, sType, legendText=""):
        """Adds a graph to the class object."""

        self.a_x.append(a_xAxis)
        self.a_y.append(a_yAxis)
        self.a_types.append(sType)
        self.a_legends.append(legendText)

        for x in a_xAxis:
            if x < self.xMin:
                self.xMin = x

            if x > self.xMax:
                self.xMax = x

        for y in a_yAxis:
            if y < self.yMin:
                self.yMin = y

            if y > self.yMax:
                self.yMax = y

        self.graphCount += 1

