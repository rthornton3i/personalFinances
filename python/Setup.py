from Vars import Vars
from TaxDict import TaxDict

from Utility import Utility

import numpy as np
import math
import random

class Setup:
    
    def __init__(self,vars,taxes):
        self.vars = vars
        self.taxes = taxes
        
        self.years = vars.base.years
        self.numInd = vars.base.numInd

        self.retAges = vars.base.retAges
        self.baseAges = vars.base.baseAges
        self.childYrs = vars.children.childYrs
        self.maxChildYr = vars.children.maxChildYr
        
        self.salBases = vars.salary.salBase
        self.salGrowth = vars.salary.salGrowth
        self.salBonus = vars.salary.salBonus
        self.prevSal = vars.salary.prevSal
        self.promotionChance = vars.salary.promotionChance
        self.promotionGrowth = vars.salary.promotionGrowth
        
        self.filingType = vars.filing.filingType.upper()
        
    def run(self):
        match self.filingType:
            case "JOINT": iters = 1
            case "SEPARATE", "SINGLE": iters = self.numInd

        self.vars.filing.iters = iters

        # Ages
        [self.vars.base.ages, \
        self.vars.children.childAges] = self.ageCalc()
        
        # Salary
        [self.vars.salary.salary, \
        self.vars.salary.income, \
        self.vars.salary.grossIncome] = self.salaryCalc()
                
        # Social Security
        self.vars.benefits.socialSecurity.ssIns = self.socialSecurityCalc()

        # Retirement
        # self.vars.taxes.totalTradRet = np.random.random((self.numInd,self.years))*1e6
        # self.vars.taxes.totalRothRet = np.random.random((self.numInd,self.years))*1e6
        # test = self.retirementCalc()
        
        return self.vars
    
    def salaryCalc(self):
        salary = np.zeros((self.numInd,self.years))

        for i in range(self.numInd):
            salary[i,0] = self.salBases[i]
            promotion = np.full(self.years,False)
            
            for j in range(1,self.years):
                if j < self.retAges[i] - self.baseAges[i]:
                    if j+1 < self.promotionChance[0]:
                        salary[i,j] = salary[i,j-1] * (1 + random.triangular(self.salGrowth[0],self.salGrowth[2],self.salGrowth[1]))
                    else:
                        if not np.all(promotion[j-(self.promotionChance[0]-1):j+1]) and random.random() < self.promotionChance[1]:
                            salary[i,j] = salary[i,j-1] * (1 + random.triangular(self.promotionGrowth[0],self.promotionGrowth[2],self.promotionGrowth[1]))
                            promotion[j] = True
                        else:
                            salary[i,j] = salary[i,j-1] * (1 + random.triangular(self.salGrowth[0],self.salGrowth[2],self.salGrowth[1]))

            salary[i] *= 1 + self.salBonus[i]
        
        match self.filingType:
            case "JOINT":   income = [np.sum(salary,0)]
            case _:         income = salary
            
        grossIncome = np.sum(salary,0)

        return salary,income,grossIncome

    def ageCalc(self):
        ages = np.zeros((self.numInd,self.years))
        childAges = np.zeros((len(self.childYrs),self.years))

        for i in range(self.years):
            for j in range(self.numInd):
                ages[j,i] = self.baseAges[j] + i
                
            for j in range(len(self.childYrs)):
                if i >= self.childYrs[j]:
                    childAges[j,i] = i - self.childYrs[j]
        
        return ages,childAges
    
    def socialSecurityCalc(self):
        ss = self.vars.benefits.socialSecurity
        
        ssWages = np.zeros((self.numInd,self.years+len(self.prevSal[0])))
        primIns = np.zeros(self.numInd)
        aime = np.zeros(self.numInd)

        ssIns = np.zeros((self.numInd,self.years))

        colYrs = np.zeros(self.numInd)
        for i in range(self.numInd):
            colYrs[i] = ss.collectionAge[i] - self.baseAges[i]
       
        wageGrowth = [random.normalvariate(ss.wageInd,ss.wageDev) for _ in range(self.years)]
        wageIndex = np.zeros((self.numInd,self.years))
        for i in range(self.numInd):
            yr = int(colYrs[i])
            wageIndex[i,yr] = ss.wageIndex

            for j in range(yr-1,-1,-1):
                wageIndex[i,j] = wageIndex[i,j+1] / (1+wageGrowth[j])

            for j in range(yr+1,self.years):
                wageIndex[i,j] = wageIndex[i,j-1] * (1+wageGrowth[j])

        match self.filingType:
            case "JOINT":       socialSecurity = self.taxes.federal.fica.ss.joint
            case "SEPARATE":    socialSecurity = self.taxes.federal.fica.ss.separate
            case "SINGLE":      socialSecurity = self.taxes.federal.fica.ss.single
            case _:             socialSecurity = self.taxes.federal.fica.ss.single # Assume Single 
       
        for i in range(self.numInd):
            # SS WAGES
            prevYrs = len(self.prevSal[i])
            for j in range(prevYrs):
                yrInd = colYrs[i] - j
                growthFactor = random.normalvariate(ss.wageInd)
                
                ssWages[i,j] = self.prevSal[i][j]
                ssWages[i,j] *= growthFactor
                
                if ssWages[i,j] > socialSecurity.maxSal:
                    ssWages[i,j] = socialSecurity.maxSal           
            
            for j in range(self.years):
                yrInd = colYrs[i] - (j + prevYrs)
                growthFactor = math.exp(ss.wageInd * yrInd)
                
                ssWages[i,j+prevYrs] = self.vars.salary.salary[i,j]
                ssWages[i,j+prevYrs] *= growthFactor
                
                if ssWages[i,j+prevYrs] > socialSecurity.maxSal:
                    ssWages[i,j+prevYrs] = socialSecurity.maxSal

            ssWages[i] = np.sort(ssWages[i])[-35:]
            aime[i] = np.average(ssWages[i]) / 12
            
            # BEND POINTS
            tempAime = aime[i]
            prevBend = 0
            for k in range(3):
                if k < 2:
                    bendPt = ss.bendPts[k]
                else:
                    bendPt = 1e9
                
                if aime[i] > bendPt:
                    bracketAmt = ss.bendPerc[k] * (bendPt - prevBend)
                else:
                    bracketAmt = ss.bendPerc[k] * tempAime
               
                primIns[i] += bracketAmt
                tempAime -= bracketAmt
                
                prevBend = bendPt
           
            # FULL RETIREMENT AGE ADJUSTMENTS
            earlyClaim = 0
            lateClaim = 0
            if ss.collectionAge[i] < ss.fullRetAge:
                earlyClaim = (ss.fullRetAge - ss.collectionAge[i]) * 12
            else:
                lateClaim = (ss.collectionAge[i] - ss.fullRetAge) * 12
                if (lateClaim > 36):
                    lateClaim = 36
               
            if (earlyClaim > 36):
                primIns[i] -= ((36 * ss.earlyRetAge[0]) * primIns[i]) + (((earlyClaim - 36) * ss.earlyRetAge[1]) * primIns[i])
            else:
                primIns[i] -= (earlyClaim * ss.earlyRetAge[0]) * primIns[i]
           
            primIns[i] += (lateClaim * ss.lateRetAge) * primIns[i]
            
            # COLA ADJUSTMENTS
            k = 1
            for j in range(colYrs[i].astype(int),self.years):
                ssIns[i,j] = primIns[i]# * math.exp(ss.cola * k) * 12
                k += 1
        
        # match self.filingType:
        #     case "JOINT": ssIns = np.sum(primIns, 1)

        return ssIns

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
                    print(ages[i,j])
                    print(distributionYrs(ages[i,j]))
                    tradWithdrawal[j] += totalTrad[i,j] / distributionYrs(ages[i,j])
                    rothWithdrawal[j] += totalRoth[i,j] / distributionYrs(ages[i,j])

        return tradWithdrawal, rothWithdrawal