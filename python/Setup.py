from Vars import Vars
from TaxDict import TaxDict

import numpy as np
import pandas as pd

class Setup:
    
    def __init__(self,vars:Vars,taxes:TaxDict):
        self.vars:Vars = vars
        self.taxes:TaxDict = taxes
        
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
        child = self.vars.children
        base = self.vars.base
        base.ages = self.ages
        base.isRetire = self.isRetire
        child.childAges = self.childAges
        child.isKids = self.isKids        
        
        # Salary
        self.salaryCalc()
        sal = self.vars.salary 
        sal.salary = self.salary
        sal.income = self.income
        sal.inflation = self.inflation
        sal.summedInflation = self.summedInflation
        child.childInflation = self.childInflation
                
        # Social Security
        self.socialSecurityCalc()
        self.vars.benefits.socialSecurity.ssIns = self.ssIns
        
        return self.vars
    
    def salaryCalc(self):
        base = self.vars.base
        sal = self.vars.salary
        child = self.vars.children

        self.salary = np.zeros((self.numInd,self.years))

        for i in range(self.numInd):
            if sal.salOpt[i].upper() == 'CUSTOM':
                ind = 0 if sal.salCustom.shape[1] != self.numInd else i
                self.salary[i] = np.interp(np.arange(self.years),sal.salCustom.index,sal.salCustom.iloc[:,ind])
            else:
                ## ASSIGN A BASE SALARY
                ind = 0 if sal.salBase.shape[0] != self.numInd else i
                self.salary[i,0] = sal.salBase[ind]
                promotion = np.full(self.years,False)
                
                ## ACCOUNT FOR PROMOTION BASED ON CHANCE AND WAIT PERIOD
                for j in range(1,self.years):
                    if j < base.retAges[i] - base.baseAges[i]:
                        noPrevPromotion = j+1 > sal.promotionWaitPeriod and not np.any(promotion[j-(sal.promotionWaitPeriod-1):j+1])
                        receivePromotion = np.random.random() < sal.promotionChance

                        if noPrevPromotion and receivePromotion:
                            self.salary[i,j] = self.salary[i,j-1] * (1 + np.random.triangular(sal.promotionGrowth[0],sal.promotionGrowth[1],sal.promotionGrowth[2]))
                            promotion[j] = True
                        else:
                            self.salary[i,j] = self.salary[i,j-1] * (1 + np.random.triangular(sal.salGrowth[0],sal.salGrowth[1],sal.salGrowth[2]))

                ## ACCOUNT FOR BONUS
                if np.sum(sal.salBonus) > 0:
                    self.salary[i] *= 1 + np.random.triangular(sal.salBonus[0],sal.salBonus[1],sal.salBonus[2])
        
        ## CALCULATE INCOME BASED ON FILING
        match self.filingType:
            case "JOINT":   self.income = np.array([np.sum(self.salary,0)])
            case _:         self.income = self.salary

        ## CALCULATE INFLATION
        self.inflation = [np.random.normal(sal.wageInd,sal.wageDev) for _ in range(self.years)]
        self.inflation[0] = 0

        self.summedInflation = np.ones(self.years)
        for i in range(1,self.years):
            self.summedInflation[i] = self.summedInflation[i-1]*(1+self.inflation[i])

        self.childInflation = child.childInflationVal * self.isKids

        # pd.DataFrame(self.salary.transpose(),index=np.arange(self.years)).to_csv('Outputs/Salary.csv')
        # pd.DataFrame((self.salary/self.summedInflation).transpose(),index=np.arange(self.years)).to_csv('Outputs/Salary_noInflation.csv')

    def ageCalc(self):
        base = self.vars.base
        child = self.vars.children

        self.ages = np.zeros((self.numInd,self.years))
        self.childAges = np.zeros((len(child.childBaseAges),self.years))
        self.isKids = np.zeros(self.years)
        self.isRetire = np.zeros((self.numInd,self.years))

        for i in range(self.years):
            for j in range(self.numInd):
                self.ages[j,i] = base.baseAges[j] + i
            
            for j,ch in enumerate(child.childBaseAges):
                self.childAges[j,i] = i + ch
        
        for ch in child.childBaseAges:
            self.isKids[max(0,-ch):max(0,-ch)+child.maxChildYr-ch] += 1

        for ind in range(self.numInd):
            self.isRetire[ind,self.ages[ind]>base.retAges[ind]] = 1
        
    def socialSecurityCalc(self):
        def propagate(vals):
            for j in range(prevYrs-1,-1,-1): # previous years
                vals[j] = vals[j+1] / (1 + wageInflation[j])

            for j in range(prevYrs+1,self.years+prevYrs): # future years
                vals[j] = vals[j-1] * (1 + wageInflation[j])

            return vals

        base  = self.vars.base
        sal = self.vars.salary
        ss      = self.vars.benefits.socialSecurity
        socialSecurity = self.taxes.federal.fica.ss.single # Use Single value
        
        self.ssIns = np.zeros((self.numInd,self.years))

        for i in range(self.numInd):
            prevSal = sal.prevSal.iloc[:,i][~pd.isna(sal.prevSal.iloc[:,i])]

            ## GET INDEX OF COLLECTION YEAR AND AT 60
            prevYrs = len(prevSal)
            colYrs = (ss.collectionAge[i] - base.baseAges[i]).astype(int)
            yrAt60 = (60 - base.baseAges[i] + prevYrs).astype(int)
            yrAt62 = (62 - base.baseAges[i] + prevYrs).astype(int)
            
            # If not turning 60
            if yrAt60 > self.years + prevYrs:
                return
                
            ## GET WAGE INDEX BASED ON FWD AND BKWD INFLATION
            wageInflation = np.concatenate([[np.random.normal(sal.wageInd,sal.wageDev) for _ in range(prevYrs)],self.inflation])
            wageIndex = np.zeros(self.years+prevYrs)
            ssMaxSal = np.zeros(np.shape(wageIndex))

            # Set "current year" to base wage index and max sal
            wageIndex[prevYrs] = ss.wageIndex
            ssMaxSal[prevYrs] = socialSecurity.maxSal

            # Interpolate wage index and max sal backwards and forwards
            wageIndex = propagate(wageIndex)
            ssMaxSal = propagate(ssMaxSal)

            wageAt60 = wageIndex[yrAt60]
            ssMaxAt60 = ssMaxSal[yrAt60]

            ## ADJUST BEND POINTS FOR CALCULATING TOTAL BENEFITS
            bendPts = np.zeros((self.years+prevYrs,len(ss.bendPts)))
            bendPts[prevYrs,:] = ss.bendPts
            bendPts = propagate(bendPts)

            bendPtsAt62 = bendPts[yrAt62,:]

            ## GET AWI BASED ON YEAR TURNED 60
            awi = np.ones(np.shape(wageIndex))
            awi[:yrAt60] = (wageAt60 / wageIndex[:yrAt60])
            
            ## GET ADJUSTED WAGES
            adjustedWages = np.ones(np.shape(wageIndex)) * ssMaxAt60

            adjWagesRaw_bkwd = prevSal.iloc[:prevYrs] * awi[:prevYrs]
            adjIndex_bkwd    = adjWagesRaw_bkwd <= ssMaxAt60
            adjustedWages[:prevYrs][adjIndex_bkwd] = adjWagesRaw_bkwd[adjIndex_bkwd]
            
            adjWagesRaw_fwd = sal.salary[i] * awi[prevYrs:]
            adjIndex_fwd    = adjWagesRaw_fwd <= ssMaxAt60
            adjustedWages[prevYrs:][adjIndex_fwd] = adjWagesRaw_fwd[adjIndex_fwd]

            # Get 35 highest paid years and average monthly earnings (AIME)
            ssWages = np.sort(adjustedWages)[-35:]
            aime    = np.average(ssWages) / 12
            primIns = 0

            ## BEND POINTS
            maxBracket = 0
            for k in range(len(ss.bendPerc)):
                minBracket = maxBracket
                maxBracket = bendPtsAt62[k]
                rateBracket = ss.bendPerc[k]
                
                if aime > maxBracket:
                    primIns += (maxBracket - minBracket) * rateBracket
                elif aime > minBracket:
                    primIns += (aime - minBracket) * rateBracket
                        
            self.ssIns[i,colYrs:] = primIns

            ## FULL RETIREMENT AGE ADJUSTMENTS
            earlyClaim = 0
            lateClaim = 0
            if ss.collectionAge[i] < ss.fullRetAge:
                earlyClaim = (ss.fullRetAge - ss.collectionAge[i]) * 12
            else:
                lateClaim = (ss.collectionAge[i] - ss.fullRetAge) * 12
                if (lateClaim > 36):
                    lateClaim = 36
            
            for j in range(colYrs,self.years):
                if (earlyClaim > 36):
                    self.ssIns[i,j] -= ((36 * ss.earlyRetAge[0]) * self.ssIns[i,j]) + (((earlyClaim - 36) * ss.earlyRetAge[1]) * self.ssIns[i,j])
                else:
                    self.ssIns[i,j] -= (earlyClaim * ss.earlyRetAge[0]) * self.ssIns[i,j]
            
                self.ssIns[i,j] += (lateClaim * ss.lateRetAge) * self.ssIns[i,j]
            
            ## COLA Adjustments
            for j in range(colYrs+1,self.years):
                self.ssIns[i,j] = self.ssIns[i,j-1] * (1 + wageInflation[j+prevYrs])
                
        self.ssIns *= 12

        # pd.DataFrame(self.ssIns.transpose(),index=np.arange(self.years)).to_csv('Outputs/SocialSecurity.csv')