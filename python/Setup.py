from Vars import Vars
from TaxDict import TaxDict

from Utility import Utility

import numpy as np

class Setup:
    
    def __init__(self,vars,taxes):
        self.vars = vars
        self.taxes = taxes
        
        self.years = vars.base.years
        self.numInd = vars.base.numInd
        
        self.filingType = vars.filing.filingType.upper()
        
    def run(self):
        match self.filingType:
            case "JOINT": iters = 1
            case "SEPARATE", "SINGLE": iters = self.numInd

        self.vars.filing.iters = iters

        # Ages
        self.ageCalc()
        self.vars.base.ages = self.ages
        self.vars.children.childAges = self.childAges
        
        # Salary
        self.salaryCalc()
        sal = self.vars.salary 
        sal.salary = self.salary
        sal.income = self.income
        sal.grossIncome = self.grossIncome
        sal.inflation = self.inflation
                
        # Social Security
        self.socialSecurityCalc()
        self.vars.benefits.socialSecurity.ssIns = self.ssIns

        # Retirement
        # self.vars.taxes.totalTradRet = np.random.random((self.numInd,self.years))*1e6
        # self.vars.taxes.totalRothRet = np.random.random((self.numInd,self.years))*1e6
        # test = self.retirementCalc()
        
        return self.vars
    
    def salaryCalc(self):
        base = self.vars.base
        sal = self.vars.salary

        self.salary = np.zeros((self.numInd,self.years))

        for i in range(self.numInd):
            """ASSIGN A BASE SALARY"""
            self.salary[i,0] = sal.salBase[i]
            promotion = np.full(self.years,False)
            
            """ACCOUNT FOR PROMOTION BASED ON CHANCE AND WAIT PERIOD"""
            for j in range(1,self.years):
                if j < base.retAges[i] - base.baseAges[i]:
                    noPrevPromotion = j+1 > sal.promotionWaitPeriod and not np.any(promotion[j-(sal.promotionWaitPeriod-1):j+1])
                    receivePromotion = np.random.random() < sal.promotionChance

                    if noPrevPromotion and receivePromotion:
                        self.salary[i,j] = self.salary[i,j-1] * (1 + np.random.triangular(sal.promotionGrowth[0],sal.promotionGrowth[1],sal.promotionGrowth[2]))
                        promotion[j] = True
                    else:
                        self.salary[i,j] = self.salary[i,j-1] * (1 + np.random.triangular(sal.salGrowth[0],sal.salGrowth[1],sal.salGrowth[2]))

            """ACCOUNT FOR BONUS"""
            self.salary[i] *= 1 + np.random.triangular(sal.salBonus[0],sal.salBonus[1],sal.salBonus[2])
        
        """CALCULATE INCOME BASED ON FILING"""
        match self.filingType:
            case "JOINT":   self.income = [np.sum(self.salary,0)]
            case _:         self.income = self.salary
            
        self.grossIncome = np.sum(self.salary,0)

        """CALCULATE INFLATION"""
        self.inflation = [np.random.normal(sal.wageInd,sal.wageDev) for _ in range(self.years)]
        self.inflation[0] = 0

    def ageCalc(self):
        base = self.vars.base
        child = self.vars.children

        self.ages = np.zeros((self.numInd,self.years))
        self.childAges = np.zeros((len(child.childYrs),self.years))

        for i in range(self.years):
            for j in range(self.numInd):
                self.ages[j,i] = base.baseAges[j] + i
                
            for j in range(len(child.childYrs)):
                if i >= child.childYrs[j]:
                    self.childAges[j,i] = i - child.childYrs[j]
    
    def socialSecurityCalc(self):
        base = self.vars.base
        ss = self.vars.benefits.socialSecurity
        sal = self.vars.salary
        socialSecurity = self.taxes.federal.fica.ss.single # Use Single value
        
        self.ssIns = np.zeros((self.numInd,self.years))

        """GET INDEX OF COLLECTION YEAR AND AT 60"""
        prevYrs = max([len(prevSal) for prevSal in sal.prevSal])

        colYrs = np.zeros(self.numInd)
        yrAt60 = np.zeros(self.numInd).astype(int)
        yrAt62 = np.zeros(self.numInd).astype(int)
        for i in range(self.numInd):
            colYrs[i] = ss.collectionAge[i] - base.baseAges[i]
            yrAt60[i] = 60 - base.baseAges[i] + prevYrs
            yrAt62[i] = 62 - base.baseAges[i] + prevYrs
       
        """GET WAGE INDEX BASED ON FWD AND BKWD INFLATION"""
        wageGrowth = [np.random.normal(sal.wageInd,sal.wageDev) for _ in range(self.years+prevYrs)]
        wageIndex = np.zeros((self.numInd,self.years+prevYrs))
        wageAt60 = np.zeros(self.numInd)

        ssMaxSal = np.zeros(np.shape(wageIndex))
        ssMaxAt60 = np.zeros(self.numInd)
        for i in range(self.numInd):
            wageIndex[i,prevYrs] = ss.wageIndex
            ssMaxSal[i,prevYrs] = socialSecurity.maxSal

            for j in range(prevYrs-1,-1,-1): # previous years
                wageIndex[i,j] = wageIndex[i,j+1] / (1+wageGrowth[j])
                ssMaxSal[i,j] = ssMaxSal[i,j+1] / (1+wageGrowth[j])

            for j in range(prevYrs+1,self.years): # future years
                wageIndex[i,j] = wageIndex[i,j-1] * (1+wageGrowth[j])
                ssMaxSal[i,j] = ssMaxSal[i,j-1] * (1+wageGrowth[j])

            wageAt60[i] = wageIndex[i,yrAt60[i]]
            ssMaxAt60[i] = ssMaxSal[i,yrAt60[i]]

        """ADJUST""" 
        bendPts = np.zeros((self.years+prevYrs,len(ss.bendPts)))
        bendPts[prevYrs,:] = ss.bendPts
        for j in range(prevYrs-1,-1,-1): # previous years
            bendPts[j,:] = bendPts[j+1,:] / (1+wageGrowth[j])

        for j in range(prevYrs+1,self.years): # future years
            bendPts[j,:] = bendPts[j-1,:] * (1+wageGrowth[j])

        bendPtsAt62 = np.zeros((self.numInd,len(ss.bendPts)))
        for i in range(self.numInd):
            bendPtsAt62[i,:] = bendPts[yrAt62[i],:]

        """GET AWI BASED ON YEAR TURNED 60"""
        awi = np.zeros(np.shape(wageIndex))
        for i in range(self.numInd):
            for j in range(yrAt60[i]-1,-1,-1):
                awi[i,j] = wageAt60[i] / wageIndex[i,j]

            for j in range(yrAt60[i],self.years+prevYrs):
                awi[i,j] = 1
        
        """GET ADJUSTED WAGES"""
        adjustedWages = np.zeros(np.shape(wageIndex))
        ssWages = np.zeros((self.numInd,35))
        aime = np.zeros(self.numInd)
        primIns = np.zeros(self.numInd)
        for i in range(self.numInd):
            for j in range(prevYrs):
                adjustedWages[i,j] = sal.prevSal[i][j] * awi[i,j] if sal.prevSal[i][j] * awi[i,j] <= ssMaxAt60[i] else ssMaxAt60[i]
            
            for j in range(self.years):
                adjustedWages[i,j+prevYrs] = self.vars.salary.salary[i][j] * awi[i,j+prevYrs] if self.vars.salary.salary[i][j] * awi[i,j+prevYrs] <= ssMaxAt60[i] else ssMaxAt60[i]

            ssWages[i,:] = np.sort(adjustedWages[i])[-35:]
            aime[i] = np.average(ssWages[i]) / 12
            
            """BEND POINTS"""
            maxBracket = 0
            for k in range(len(ss.bendPerc)):
                minBracket = maxBracket
                maxBracket = bendPtsAt62[i,k]
                rateBracket = ss.bendPerc[k]
                
                if aime[i] > maxBracket:
                    primIns[i] += (maxBracket - minBracket) * rateBracket
                elif aime[i] > minBracket:
                    primIns[i] += (aime[i] - minBracket) * rateBracket
            
            """COLA Adjustments"""
            init = True
            for j in range(colYrs[i].astype(int),self.years):
                if init:
                    self.ssIns[i,j] = primIns[i]
                    init = False
                else:
                    self.ssIns[i,j] = self.ssIns[i,j-1] * (1+wageGrowth[j+prevYrs])

            """FULL RETIREMENT AGE ADJUSTMENTS"""
            earlyClaim = 0
            lateClaim = 0
            if ss.collectionAge[i] < ss.fullRetAge:
                earlyClaim = (ss.fullRetAge - ss.collectionAge[i]) * 12
            else:
                lateClaim = (ss.collectionAge[i] - ss.fullRetAge) * 12
                if (lateClaim > 36):
                    lateClaim = 36
            
            for j in range(colYrs[i].astype(int),self.years):
                if (earlyClaim > 36):
                    self.ssIns[i,j] -= ((36 * ss.earlyRetAge[0]) * self.ssIns[i,j]) + (((earlyClaim - 36) * ss.earlyRetAge[1]) * self.ssIns[i,j])
                else:
                    self.ssIns[i,j] -= (earlyClaim * ss.earlyRetAge[0]) * self.ssIns[i,j]
            
                self.ssIns[i,j] += (lateClaim * ss.lateRetAge) * self.ssIns[i,j]

    def retirementCalc(self):
        def distributionYrs(age):
            return -0.00000684*age**4+0.00266293*age**3-0.37364604*age**2+21.78182*age-414.165

        retire = self.vars.benefits.retirement
        ages = self.vars.base.ages

        totalTrad = self.vars.taxes.totalTradRet
        totalRoth = self.vars.taxes.totalRothRet

        tradWithdrawal = np.zeros(self.years)
        rothWithdrawal = np.zeros(self.years)

        for j in range(self.years):
            for i in range(self.numInd):
                if ages[i,j] >= retire.rmdAge:
                    tradWithdrawal[j] += totalTrad[i,j] / distributionYrs(ages[i,j])
                    rothWithdrawal[j] += totalRoth[i,j] / distributionYrs(ages[i,j])

        return tradWithdrawal, rothWithdrawal