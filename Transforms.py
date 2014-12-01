#!/usr/bin/python
#######
# File: Transforms.py
# Project: Regularization
# Author: Joe Chapman
# Date: 9-8-14
# Url: https://github.com/JoeyChaps/regularization
#######

class Transform:

    def __init__ (self, num, maxFeats):

        self.bDone = True
        self.count = 3
        self.lastCount = 0
        self.transNum = 0
        self.transformDef = ""
        self.ncolumns = 0
        self.nMaxFeatures = maxFeats

        if num == 1:
            self.transNum = num
        elif num == 2:
            self.transNum = num
        elif num == 3:
            self.transNum = num
        else:
            self.transNum = None


    def getTransform(self):
        if self.transNum == 1:
            return self.tran1
        elif self.transNum == 2:
            return self.tran2
        elif self.transNum == 3:
            return self.tran3
        else:
            return None


    def getTestTransform(self):        
        if self.transNum == 1:            

            self.count = self.lastCount

            return self.tran1
        elif self.transNum == 2:            

            self.count = self.lastCount

            return self.tran2
        elif self.transNum == 3:            

            self.count = self.lastCount

            return self.tran3
        else:
            return None


    def getTransformVersion(self):

        if self.transNum:            
            sVers = str(self.transNum)

            if self.transNum > 0 & self.transNum < 4:
                sVers = sVers + "-" + str(self.count)

            return sVers
        else:
            return None
    

    def getTransformCount(self):
        return self.lastCount


    def setTransformCount(self, c):
        self.count = c


    def getTransformDef(self):
        return self.transformDef


    def getDone(self):
        return self.bDone


    def tran1(self, a_pats):

        self.bDone = False
        
        ncols = 0

        a_tranPats = []
        npats = len(a_pats)

        if (npats > 0):
            ncols = len(a_pats[0])

            if (ncols > 0):        

                sFormula = ""

                if (self.count >= 3):
                    sFormula = "1, x0, x1"
                    if (self.count >= 4):
                        sFormula = sFormula + ", x0^2"
                        if (self.count >= 5):
                            sFormula = sFormula + ", x0x1"
                            if (self.count >= 6):
                                sFormula = sFormula + ", x1^2"
                                if (self.count >= 7):
                                    sFormula = sFormula + ", x0^3"
                                    if (self.count >= 8):
                                        sFormula = sFormula + ", x0^2x1"
                                        if (self.count >= 9):
                                            sFormula = sFormula + ", x1^2x0"
                                            if (self.count >= 10):
                                                sFormula = sFormula + ", x1^3"
                                                if (self.count >= 11):
                                                    sFormula = sFormula + ", x0^4"
                                                    if (self.count >= 12):
                                                        sFormula = sFormula + ", x0^3x1"
                                                        if (self.count >= 13):
                                                            sFormula = sFormula + ", x0^2x1^2"
                                                            if (self.count >= 14):
                                                                sFormula = sFormula + ", x1^3x0"
                                                                if (self.count >= 15):
                                                                    sFormula = sFormula + ", x1^4"
                                                                    if (self.count >= 16):
                                                                        sFormula = sFormula + ", x0^5"
                                                                        if (self.count >= 17):
                                                                            sFormula = sFormula + ", x0^4x1"
                                                                            if (self.count >= 18):
                                                                                sFormula = sFormula + ", x0^3x1^2"
                                                                                if (self.count >= 19):
                                                                                    sFormula = sFormula + ", x0^2x1^3"
                                                                                    if (self.count >= 20):
                                                                                        sFormula = sFormula + ", x1^4x0"
                                                                                        if (self.count >= 21):
                                                                                            sFormula = sFormula + ", x1^5"

                self.transformDef = sFormula
                
                for p in range(0, npats):

                    x0 = a_pats[p][0]
                    x1 = a_pats[p][1]

                    x0_2 = x0 * x0
                    x1_2 = x1 * x1

                    x0_3 = x0 * x0_2
                    x1_3 = x1 * x1_2

                    x0_4 = x0 * x0_3
                    x1_4 = x1 * x1_3

                    x0_5 = x0 * x0_4
                    x1_5 = x1 * x1_4

                    a_row = []

                    if (self.count >= 3):
                        a_row = [1, x0, x1]
                        if (self.count >= 4):
                            a_row.append(x0_2)
                            if (self.count >= 5):
                                a_row.append(x0 * x1)
                                if (self.count >= 6):
                                    a_row.append(x1_2)
                                    if (self.count >= 7):
                                        a_row.append(x0_3)
                                        if (self.count >= 8):
                                            a_row.append(x0_2 * x1)
                                            if (self.count >= 9):
                                                a_row.append(x1_2 * x0)
                                                if (self.count >= 10):
                                                    a_row.append(x1_3)
                                                    if (self.count >= 11):
                                                        a_row.append(x0_4)
                                                        if (self.count >= 12):
                                                            a_row.append(x0_3 * x1)
                                                            if (self.count >= 13):
                                                                a_row.append(x0_2 * x1_2)
                                                                if (self.count >= 14):
                                                                    a_row.append(x1_3 * x0)
                                                                    if (self.count >= 15):
                                                                        a_row.append(x1_4)
                                                                        if (self.count >= 16):
                                                                            a_row.append(x0_5)
                                                                            if (self.count >= 17):
                                                                                a_row.append(x0_4 * x1)
                                                                                if (self.count >= 18):
                                                                                    a_row.append(x0_3 * x1_2)
                                                                                    if (self.count >= 19):
                                                                                        a_row.append(x0_2 * x1_3)
                                                                                        if (self.count >= 20):
                                                                                            a_row.append(x1_4 * x0)
                                                                                            if (self.count >= 21):
                                                                                                a_row.append(x1_5)
                            
                    a_tranPats.append(a_row)

                self.lastCount = self.count
                self.count += 1

                if (self.count > self.nMaxFeatures):
                    self.bDone = True                    

        return list(a_tranPats)


    def tran2(self, a_pats):

        self.bDone = False
        
        ncols = 0

        a_tranPats = []
        npats = len(a_pats)

        if (npats > 0):
            ncols = len(a_pats[0])

            if (ncols > 0):        

                sFormula = ""

                if (self.count >= 1):
                    sFormula = "1, x0, x1"
                    if (self.count >= 2):
                        sFormula = sFormula + ", x0^2, x0x1, x1^2"
                        if (self.count >= 3):

                            sFormula = sFormula + \
                                       ", x0^3, x0^2x1, x1^2x0, x1^3"
                            
                            if (self.count >= 4):

                                sFormula = sFormula + \
                                           ", x0^4, x0^3x1, x0^2x1^2, x1^3x0, \
                                            x1^4"

                                if (self.count >= 5):

                                    sFormula = sFormula + \
                                               ", x0^5, x0^4x1, x0^3x1^2, \
                                                x0^2x1^3, x1^4x0, x1^5"

                self.transformDef = sFormula
                
                for p in range(0, npats):

                    x0 = a_pats[p][0]
                    x1 = a_pats[p][1]

                    x0_2 = x0 * x0
                    x1_2 = x1 * x1

                    x0_3 = x0 * x0_2
                    x1_3 = x1 * x1_2

                    x0_4 = x0 * x0_3
                    x1_4 = x1 * x1_3

                    x0_5 = x0 * x0_4
                    x1_5 = x1 * x1_4

                    a_row = []

                    if (self.count >= 1):
                        a_row = [1, x0, x1]
                        if (self.count >= 2):
                            a_row.append([x0_2, x0 * x1, x1_2])
                            if (self.count >= 3):
                                a_row.append([x0_3, x0_2 * x1, x1_2 * x0, x1_3])
                                if (self.count >= 4):

                                    a_row.append([x0_4, x0_3 * x1, x0_2 * x1_2, 
                                                  x1_3 * x0, x1_4])
                                    
                                    if (self.count >= 5):
                                        
                                        a_row.append([x0_5, x0_4 * x1, x0_3 * 
                                                      x1_2, x0_2 * x1_3, x1_4 
                                                      * x0, x1_5])
                            
                    a_tranPats.append(a_row)

                self.lastCount = self.count
                self.count += 1

                if (self.count > 5):
                    self.bDone = True                    

        return list(a_tranPats)


    def tran3(self, a_pats):

        self.bDone = False
        
        ncols = 0

        a_tranPats = []
        npats = len(a_pats)
        

        self.transformDef = "x0,x0^2,x0^3,x0^4,x0^5"
        
        for p in range(0, npats):

            x0 = a_pats[p][0]
            x0_2 = x0 * x0
            x0_3 = x0 * x0_2
            x0_4 = x0 * x0_3
            x0_5 = x0 * x0_4

            a_row = [x0, x0_2, x0_3, x0_4, x0_5]
                    
            a_tranPats.append(a_row)

        self.lastCount = self.count
        self.count += 1

        if (self.count > self.nMaxFeatures):
            self.bDone = True                    

        return list(a_tranPats)
            	