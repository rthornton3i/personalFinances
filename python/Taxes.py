from Utility import Utility

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Taxes:
    def __init__(self, vars, taxes):
        self.vars = vars
        self.taxes = taxes
        
        self.years = vars.base.years
        self.numInd = vars.base.numInd
        self.iters = self.vars.filing.iters
        self.retAges = vars.base.retAges
        self.baseAges = vars.base.baseAges
        self.ages = vars.base.ages

        self.income = vars.salary.income
        self.salary = vars.salary.salary
        self.inflation = vars.salary.summedInflation
        self.childInflation = vars.children.childInflation

        self.totalExpenses = vars.expenses.totalExpenses
        
        self.filingType = vars.filing.filingType.upper()
        self.filingState = vars.filing.filingState.upper()
        
        self.isKids = self.vars.children.isKids
        self.childBaseAges = self.vars.children.childBaseAges
        
    def run(self):  
        taxes = self.vars.taxes
        benefits = self.vars.benefits
        savings = self.vars.savings

        federal = taxes.federal
        state = taxes.state
        health = benefits.health
        retirement = benefits.retirement

        self.expenses = pd.DataFrame(0,index=np.arange(self.years),columns=savings.earnings.columns)
        self.savings = pd.DataFrame(0,index=np.arange(self.years),columns=savings.earnings.columns)

#      Benefits
        self.healthCalc()
        health.healthDed = self.healthDed
        health.healthBen = self.healthBen
        
#      Retirement
        self.perc401 = np.zeros((self.numInd,self.years))
        self.cont401 = np.zeros((self.numInd,self.years))
        
        retirement.traditional.contribution = self.retContCalc(self.vars.benefits.retirement.traditional)
        retirement.roth.contribution = self.retContCalc(self.vars.benefits.retirement.roth)
        retirement.match.contribution = self.matchContCalc(self.vars.benefits.retirement.match)
        
        self.retirementWithdrawalCalc()
        self.vars.benefits.retirement.traditional.withdrawal = self.tradWithdrawal
        self.vars.benefits.retirement.roth.withdrawal = self.rothWithdrawal

#      Social Security
        self.ssTaxCalc()
        benefits.socialSecurity.taxableBenefits = self.taxableBenefits
        # plt.plot(self.ssTax)

#      Deduction/Exemptions
        self.itemDedCalc()
        federal.deductions.itemized.itemDedFed = self.itemDedFed
        state.deductions.itemized.itemDedState = self.itemDedState
        # plt.plot(self.itemDedFed[0])
        # plt.plot(self.itemDedState[0])
        
        self.stdDedCalc()
        federal.deductions.standard.stdDedFed = self.stdDedFed
        state.deductions.standard.stdDedState = self.stdDedState
        # plt.plot(self.stdDedFed[0])

        self.exemptCalc()
        federal.exemptions.exemptFed = self.exemptFed
        state.exemptions.persExempt.persExemptState = self.persExemptState
        state.exemptions.childExempt.childExemptState = self.childExemptState
        # plt.plot(self.persExemptState[0])

#      Gross Earnings
        self.grossEarnCalc()
        federal.grossIncomeFed = self.grossIncomeFed
        state.grossIncomeState = self.grossIncomeState
        # plt.plot(self.grossIncomeFed[0])
        # plt.plot(self.grossIncomeState[0])

#      State Taxes
        self.slTaxCalc()
        state.saltTaxes = self.saltTaxes
        # plt.plot(self.vars.taxes.state.saltTaxes[0])

#      Gross Earnings (Update)
        self.itemDedCalc()
        federal.deductions.itemized.itemDedFed = self.itemDedFed
        state.deductions.itemized.itemDedState = self.itemDedState
        
        self.grossEarnCalc()
        federal.grossIncomeFed = self.grossIncomeFed
        state.grossIncomeState = self.grossIncomeState
        # plt.plot(self.grossIncomeFed[0])
        # plt.plot(self.grossIncomeState[0])
        # plt.show()
        
#      Federal Taxes
        self.fedTaxCalc()
        federal.fedTax  = self.fedTax
        federal.ficaTax = self.ficaTax
        # plt.plot(federal.fedTax[0])
        # plt.show()
        
#      Net self.income    
        self.netIncCalc()                     
        taxes.totalTaxes    = self.totalTaxes
        taxes.totalDeducted = self.totalDeducted
        taxes.totalWithheld = self.totalWithheld
        taxes.netIncome = self.netIncome
        taxes.netCash   = self.netCash
        retirement.netTradCont = self.netTradCont
        retirement.netRothCont = self.netRothCont
        # plt.plot(taxes.netCash)
        # plt.show()

        """ADD RETIREMENT TO TAXABLE INCOME"""
        self.savingsCalc()
        savings.expenses = self.expenses
        savings.savings = self.savings

        return self.vars
    
    def healthCalc(self):   
        health = self.vars.benefits.health

        self.healthDed = np.zeros((self.iters,self.years))
        self.healthBen = np.zeros((self.iters,self.years))        
        
        hsa = np.zeros((self.iters,self.years))
        fsa = np.zeros((self.iters,self.years))
        hra = np.zeros((self.iters,self.years))
        medicalPrem = np.zeros((self.iters,self.years))
        visionPrem  = np.zeros((self.iters,self.years))
        dentalPrem  = np.zeros((self.iters,self.years))
        
        for i in range(self.iters):
            retire = min(self.retAges[i] - self.baseAges[i],self.years)
            for j in range(retire):
                """INFLATION"""
                hsa[i,j] = (health.hsa * self.inflation[j]) * (1 + self.childInflation[j])
                fsa[i,j] = (health.fsa * self.inflation[j]) * (1 + self.childInflation[j])
                hra[i,j] = (health.hra * self.inflation[j]) * (1 + self.childInflation[j])

                medicalPrem[i,j] = (health.medicalPrem * self.inflation[j]) * (1 + self.childInflation[j])
                visionPrem[i,j]  = (health.visionPrem * self.inflation[j]) * (1 + self.childInflation[j])
                dentalPrem[i,j]  = (health.dentalPrem * self.inflation[j]) * (1 + self.childInflation[j])

        # Post-retirement

        self.healthDed  = np.sum((hsa,fsa,hra),0)
        self.healthBen  = np.sum((medicalPrem,visionPrem,dentalPrem),0)
    
    def retContCalc(self,retirement):        
        retire = self.vars.benefits.retirement

        ret401Perc = np.zeros((self.numInd,self.years))
        
        for i in range(self.numInd):
            for j in range(self.years):
                ret401Perc[i,j] = retirement.basePerc
        
        contribution = np.multiply(ret401Perc,self.salary)
        self.perc401 = np.sum((self.perc401,ret401Perc),0)
        self.cont401 = np.sum((self.cont401,contribution),0)

        for i in range(self.numInd):
            for j in range(self.years):
                maxCont = (retire.maxSelfCont + retire.maxCatchUpCont if self.vars.base.ages[i,j] >= retire.catchUpAge else retire.maxSelfCont) * self.inflation[j]
                if self.cont401[i,j] > maxCont:
                    self.cont401[i,j] = maxCont
                    contribution[i,j] = maxCont
        
        return contribution
    
    def matchContCalc(self, retirement):  
        retire = self.vars.benefits.retirement

        match401Perc = np.zeros((self.numInd,self.years))
        
        for i in range(self.numInd):
            for j in range(self.years):
                match401Perc[i,j] = self.perc401[i,j] / 2 if self.perc401[i,j] <= retirement.maxPerc else retirement.maxPerc
                match401Perc[i,j] += retirement.basePerc if i == 1 else 0 # ONLY INDIVIDUAL 1
        
        contribution =  np.multiply(match401Perc,self.salary)
        self.cont401 = np.sum((self.cont401,contribution),0)
        
        for i in range(self.numInd):
            for j in range(self.years):
                maxCont = (retire.maxTotalCont + retire.maxCatchUpCont if self.vars.base.ages[i,j] >= retire.catchUpAge else retire.maxTotalCont) * self.inflation[j]
                if self.cont401[i,j] > maxCont:
                    contribution[i,j] -= self.cont401[i,j] - maxCont
        
        return contribution

    def ssTaxCalc(self):  
        ss = self.vars.benefits.socialSecurity

        self.taxableBenefits = np.zeros((self.iters,self.years))

        match self.filingType:
            case "JOINT":    socialSecurity = self.taxes.federal.ss.joint
            case "SEPARATE": socialSecurity = self.taxes.federal.ss.separate
            case "SINGLE":   socialSecurity = self.taxes.federal.ss.single
            case _:          socialSecurity = self.taxes.federal.ss.single # Assume Single 
         
        for i in range(self.iters):
            for j in range(self.years):
                combinedIncome = self.salary[i,j] + (ss.ssIns[i,j] / 2)
                for k in range(len(socialSecurity.bracketMax)):
                    if combinedIncome < socialSecurity.bracketMax[k]:
                        self.taxableBenefits[i,j] = socialSecurity.bracketPerc[k] * ss.ssIns[i,j]

    def retirementWithdrawalCalc(self):
        def distributionYrs(age):
            return -0.00000684*age**4+0.00266293*age**3-0.37364604*age**2+21.78182*age-414.165
         
        savings = self.vars.savings
        accounts = self.vars.accounts
        accountType = accounts.accountSummary.accountType
        ret = self.vars.benefits.retirement

        self.netTradCont = np.zeros(self.years)
        self.netRothCont = np.zeros(self.years)
        self.tradWithdrawal = np.zeros((self.numInd,self.years))
        self.rothWithdrawal = np.zeros((self.numInd,self.years))

        for j in range(self.years):
            for accName,_ in savings.earnings.items():
                """PREVIOUS YEARS BALANCE"""
                match str(accountType.loc[accName]).upper():
                    case 'ROTH'|'TRAD':
                        for i in range(self.numInd):
                            self.netTradCont[j] += ret.traditional.contribution[i,j] + ret.match.contribution[i,j]
                            self.netRothCont[j] += ret.roth.contribution[i,j]
                            
                        if j == 0:
                            self.savings.loc[0,accName] += accounts.accountSummary.baseSavings.loc[accName]
                        else:
                            self.savings.loc[j,accName] += self.savings.loc[j-1,accName]
                
                """ADD CONTRIBUTIONS"""
                match str(accountType.loc[accName]).upper():
                    case 'ROTH': self.savings.loc[j,accName] += self.netRothCont[j]
                    case 'TRAD': self.savings.loc[j,accName] += self.netTradCont[j]

                """ADD EARNINGS"""
                match str(accountType.loc[accName]).upper():
                    case 'ROTH'|'TRAD':
                        if j > 0:
                            self.savings.loc[j,accName] += savings.earnings.loc[j,accName] * self.savings.loc[j-1,accName]

                """SUBTRACT DISTRIBTUIONS"""
                for i in range(self.numInd):
                    if self.ages[i,j] >= ret.rmdAge:
                        match str(accountType.loc[accName]).upper():
                            case 'ROTH': 
                                dist = np.sum(self.savings.loc[j,accName] / distributionYrs(self.ages[i,j]))
                                self.rothWithdrawal[i,j] = dist
                                self.savings.loc[j,accName] -= dist
                            case 'TRAD': 
                                dist = np.sum(self.savings.loc[j,accName] / distributionYrs(self.ages[i,j]))
                                self.tradWithdrawal[i,j] = dist
                                self.savings.loc[j,accName] -= dist
    
    def itemDedCalc(self):
        itemDed = self.taxes.federal.deductions.itemized
        house = self.vars.expenses.house
        saltTaxes = self.vars.taxes.state.saltTaxes

        mortInt = np.zeros((self.iters,self.years))
        charDon = np.zeros((self.iters,self.years))
        slpDed = np.zeros((self.iters,self.years))
        
        self.itemDedFed = np.zeros((self.iters,self.years))
        self.itemDedState = np.zeros((self.iters,self.years))

        for i in range(self.iters):
            for j in range(self.years):
                # FEDERAL
                # SLP Taxes
                if len(saltTaxes) > 0:
                    slpDed[i,j] = (self.inflation[j] * itemDed.maxSalt) / self.iters if saltTaxes[i,j] > (self.inflation[j] * itemDed.maxSalt) / self.iters else saltTaxes[i,j]
                else:
                    slpDed[i,j] = 0
                
                # Mortgage Interest
                if house.houseBal[j] < (self.inflation[j] * itemDed.maxHouse) / self.iters:
                    mortInt[i,j] = house.houseInt[j] / self.iters
                else:
                    mortInt[i,j] = ((house.houseInt[j] / house.houseBal[j]) * (self.inflation[j] * itemDed.maxHouse)) / self.iters
                
                # Charitable Donations
                charDon[i,j] = self.totalExpenses.charity[j] / self.iters
                
                self.itemDedFed[i,j] = slpDed[i,j] + mortInt[i,j] + charDon[i,j]
                
                # STATE
                match self.filingState:
                    case "NJ": self.itemDedState[i,j] = 0
                    case "MD": self.itemDedState[i,j] = 0
    
    def stdDedCalc(self):
        dedFed = self.taxes.federal.deductions.standard

        self.stdDedFed = np.zeros((self.iters,self.years))
        self.stdDedState = np.zeros((self.iters,self.years))
                
        for i in range(self.iters):
            for j in range(self.years):
                # FEDERAL
                self.stdDedFed[i,j] = ((self.inflation[j] * dedFed.maxFed) * self.numInd) / self.iters
                
                # STATE
                match self.filingState:
                    case "NJ": 
                        self.stdDedState[i,j] = 0                
                    case "MD":
                        dedState = self.taxes.state.md.deductions.standard

                        self.stdDedState[i,j] = dedState.basePerc * self.income[i,j]

                        if self.stdDedState[i,j] < (self.inflation[j] * dedState.stdDedMin) / self.iters:
                            self.stdDedState[i,j] = (self.inflation[j] * dedState.stdDedMin) / self.iters
                        elif self.stdDedState[i,j] > (self.inflation[j] * dedState.stdDedMax) / self.iters:
                            self.stdDedState[i,j] = (self.inflation[j] * dedState.stdDedMax) / self.iters
                    
                    case "AK"| "FL"| "NV"| "NH"| "SD"| "TN"| "TX"| "WA"| "WY":
                        self.stdDedState[i,j] = 0
    
    def exemptCalc(self):
        fedExempt = self.taxes.federal.exemptions

        self.exemptFed = np.zeros((self.iters,self.years))
        self.persExemptState = np.zeros((self.iters,self.years))
        self.childExemptState = np.zeros((self.iters,self.years))
        
        for i in range(self.iters):
            for j in range(self.years):
                # FEDERAL
                self.exemptFed[i,j] = 0
                
                # STATE
                match self.filingState:
                    case "NJ":
                        match self.filingType:
                            case "JOINT":
                                persExempt = self.taxes.state.nj.exemptions.persExempt.joint
                                childExempt = self.taxes.state.nj.exemptions.childExempt.joint
                            case "SEPARATE":
                                persExempt = self.taxes.state.nj.exemptions.persExempt.separate
                                childExempt = self.taxes.state.nj.exemptions.childExempt.separate
                            case "SINGLE":
                                persExempt = self.taxes.state.nj.exemptions.persExempt.single
                                childExempt = self.taxes.state.nj.exemptions.childExempt.single
                            case _: # Assume Single
                                persExempt = self.taxes.state.nj.exemptions.persExempt.single
                                childExempt = self.taxes.state.nj.exemptions.childExempt.single                   
                                
                        for k in range(len(persExempt.bracketMax)):
                            if self.income[i,j] < (self.inflation[j] * persExempt.bracketMax[k]):
                                self.persExemptState[i,j] = (self.inflation[j] * persExempt.bracketAmt[k])                               
                                break
                        
                        for _ in range(int(self.isKids[j])):
                            for k in range(len(childExempt.bracketMax)):
                                if self.income[i,j] < (self.inflation[j] * childExempt.bracketMax[k]):
                                    self.childExemptState[i,j] += (self.inflation[j] * childExempt.bracketAmt[k]) / self.iters
                                    break
                    
                    case "MD":
                        match self.filingType:
                            case "JOINT":
                                persExempt = self.taxes.state.md.exemptions.persExempt.joint
                                childExempt = self.taxes.state.md.exemptions.childExempt.joint
                            case "SEPARATE":
                                persExempt = self.taxes.state.md.exemptions.persExempt.separate
                                childExempt = self.taxes.state.md.exemptions.childExempt.separate
                            case "SINGLE":
                                persExempt = self.taxes.state.md.exemptions.persExempt.single
                                childExempt = self.taxes.state.md.exemptions.childExempt.single
                            case _: # Assume Single
                                persExempt = self.taxes.state.md.exemptions.persExempt.single
                                childExempt = self.taxes.state.md.exemptions.childExempt.single
                        
                        for k in range(len(persExempt.bracketMax)):
                            if self.income[i,j] < (self.inflation[j] * persExempt.bracketMax[k]):
                                self.persExemptState[i,j] = (self.inflation[j] * persExempt.bracketAmt[k])
                                break
                        
                        for _ in range(int(self.isKids[j])):
                            for k in range(len(childExempt.bracketMax)):
                                if self.income[i,j] < (self.inflation[j] * childExempt.bracketMax[k]):
                                    self.childExemptState[i,j] += (self.inflation[j] * childExempt.bracketAmt[k]) / self.iters
                                    break
                    
                    case "AK"| "FL"| "NV"| "NH"| "SD"| "TN"| "TX"| "WA"| "WY":
                        self.persExemptState[i,j] = 0
                        self.childExemptState[i,j] = 0
    
    def grossEarnCalc(self):
        itemDedFed = self.vars.taxes.federal.deductions.itemized.itemDedFed
        itemDedState = self.vars.taxes.state.deductions.itemized.itemDedState

        stdDedFed = self.vars.taxes.federal.deductions.standard.stdDedFed
        stdDedState = self.vars.taxes.state.deductions.standard.stdDedState

        exemptFed = self.vars.taxes.federal.exemptions.exemptFed
        persExemptState = self.vars.taxes.state.exemptions.persExempt.persExemptState
        childExemptState = self.vars.taxes.state.exemptions.childExempt.childExemptState

        contribution = self.vars.benefits.retirement.traditional.contribution
        healthDed = self.vars.benefits.health.healthDed
        healthBen = self.vars.benefits.health.healthBen

        self.grossIncomeFed = np.zeros((self.iters,self.years))
        self.grossIncomeState = np.zeros((self.iters,self.years))

        for i in range(self.iters):
            for j in range(self.years):
                # FEDERAL
                self.grossIncomeFed[i,j] = self.income[i,j] + self.taxableBenefits[i,j] + self.tradWithdrawal[i,j] - (contribution[i,j] + healthDed[i,j] + healthBen[i,j]) 
                self.grossIncomeFed[i,j] -= itemDedFed[i,j] if itemDedFed[i,j] > stdDedFed[i,j] else stdDedFed[i,j]
                
                # STATE
                self.grossIncomeState[i,j] = self.income[i,j]
                match self.filingState:
                    case "AK"| "FL"| "NV"| "NH"| "SD"| "TN"| "TX"| "WA"| "WY":
                        pass
                    case "NJ"|"CA":
                        self.grossIncomeState[i,j] -= (contribution[i,j] + persExemptState[i,j] + childExemptState[i,j]) 
                    case _:
                        self.grossIncomeState[i,j] -= (contribution[i,j] + persExemptState[i,j] + childExemptState[i,j] + healthDed[i,j])

                match self.filingState:
                    case "NJ":
                        self.grossIncomeState[i,j] += self.tradWithdrawal[i,j]

                match self.filingState:
                    case "CO"| "CT"| "KS"| "MN"| "MO"| "MT"| "NE"| "NM"| "ND"| "RI"| "UT"| "VT"| "WV":
                        self.grossIncomeState[i,j] += self.taxableBenefits[i,j]
                
                match self.filingState:
                    case "AK"| "FL"| "NV"| "NH"| "SD"| "TN"| "TX"| "WA"| "WY":
                        pass
                    case _:
                        self.grossIncomeState[i,j] -= itemDedState[i,j] if itemDedState[i,j] > stdDedState[i,j] else stdDedState[i,j]
                
                self.grossIncomeFed[i,j] = 0 if self.grossIncomeFed[i,j] < 0 else self.grossIncomeFed[i,j]
                self.grossIncomeState[i,j] = 0 if self.grossIncomeState[i,j] < 0 else self.grossIncomeState[i,j]
    
    def slTaxCalc(self):
        house = self.vars.expenses.house
        
        stateTax = np.zeros((self.iters,self.years))
        localTax = np.zeros((self.iters,self.years))
        propTax = np.zeros((self.iters,self.years))

        self.saltTaxes = np.zeros((self.iters,self.years))

        grossIncomeState = self.vars.taxes.state.grossIncomeState
        
        for i in range(self.iters):
            match self.filingState:
                case "NJ":
                    match self.filingType:
                        case "JOINT":     state = self.taxes.state.nj.state.joint
                        case "SEPARATE":  state = self.taxes.state.nj.state.separate
                        case "SINGLE":    state = self.taxes.state.nj.state.single
                        case _:           state = self.taxes.state.nj.state.single # Assume Single

                    local = self.taxes.state.nj.local
                case "MD":
                    match self.filingType:
                        case "JOINT":     state = self.taxes.state.md.state.joint
                        case "SEPARATE":  state = self.taxes.state.md.state.separate
                        case "SINGLE":    state = self.taxes.state.md.state.single
                        case _:           state = self.taxes.state.md.state.single # Assume Single

                    local = self.taxes.state.md.local
                case "AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY":
                    state = self.taxes.state.none.state.none
                    local = self.taxes.state.none.local
                case _:
                    state = self.taxes.state.none.state.none
                    local = self.taxes.state.none.local
            
            for j in range(self.years):
                maxBracket = 0
                for k in range(len(state.bracketMax)):
                    minBracket = maxBracket
                    maxBracket = (self.inflation[j] * state.bracketMax[k])
                    rateBracket = state.bracketPerc[k]
                    
                    if grossIncomeState[i,j] > maxBracket:
                        stateTax[i,j] += (maxBracket - minBracket) * rateBracket
                    elif grossIncomeState[i,j] > minBracket:
                        stateTax[i,j] += (grossIncomeState[i,j] - minBracket) * rateBracket

                
                localTax[i,j] = grossIncomeState[i,j] * local.localPerc
                propTax[i,j] = house.houseWth[j] * house.propTax
                
                self.saltTaxes[i,j] += stateTax[i,j] + localTax[i,j] + propTax[i,j]
    
    def fedTaxCalc(self):    
        self.fedTax = np.zeros((self.iters,self.years))
        self.ficaTax = np.zeros((self.iters,self.years))

        grossIncomeFed = self.vars.taxes.federal.grossIncomeFed
            
        match self.filingType:
            case "JOINT":    
                federal = self.taxes.federal.federal.joint
                medicare = self.taxes.federal.fica.med.joint
                socialSecurity = self.taxes.federal.fica.ss.joint
            case "SEPARATE": 
                federal = self.taxes.federal.federal.separate
                medicare = self.taxes.federal.fica.med.separate
                socialSecurity = self.taxes.federal.fica.ss.separate
            case "SINGLE":   
                federal = self.taxes.federal.federal.single
                medicare = self.taxes.federal.fica.med.single
                socialSecurity = self.taxes.federal.fica.ss.single
            case _: # Assume Single        
                federal = self.taxes.federal.federal.single 
                medicare = self.taxes.federal.fica.med.single
                socialSecurity = self.taxes.federal.fica.ss.single
        
        for i in range(self.iters):
            for j in range(self.years):                
                # Federal Tax
                maxBracket = 0
                for k in range(len(federal.bracketMax)):
                    minBracket = maxBracket
                    maxBracket = (self.inflation[j] * federal.bracketMax[k])
                    rateBracket = federal.bracketPerc[k]
                    
                    if grossIncomeFed[i,j] > maxBracket:
                        self.fedTax[i,j] += (maxBracket - minBracket) * rateBracket
                    elif (grossIncomeFed[i,j] > minBracket):
                        self.fedTax[i,j] += (grossIncomeFed[i,j] - minBracket) * rateBracket
                
                # SS Tax
                if grossIncomeFed[i,j] < (self.inflation[j] * socialSecurity.maxSal):
                    self.ficaTax[i,j] += grossIncomeFed[i,j] * socialSecurity.rate
                else:
                    self.ficaTax[i,j] += (self.inflation[j] * socialSecurity.maxSal) * socialSecurity.rate
                
                # Medicare Tax
                if grossIncomeFed[i,j] < (self.inflation[j] * medicare.maxSal):
                    self.ficaTax[i,j] += grossIncomeFed[i,j] * medicare.rate
                else:
                    self.ficaTax[i,j] += (self.inflation[j] * medicare.maxSal) * medicare.rate
                    self.ficaTax[i,j] += (grossIncomeFed[i,j] - (self.inflation[j] * medicare.maxSal)) * medicare.addRate
    
    def netIncCalc(self):
        loans = self.vars.loans
        ret = self.vars.benefits.retirement
        ss = self.vars.benefits.socialSecurity

        fedTax = self.vars.taxes.federal.fedTax
        ficaTax = self.vars.taxes.federal.ficaTax
        saltTaxes = self.vars.taxes.state.saltTaxes

        healthDed = self.vars.benefits.health.healthDed
        healthBen = self.vars.benefits.health.healthBen

        self.totalTaxes = np.zeros(self.years)
        self.totalDeducted = np.zeros(self.years)
        self.totalWithheld = np.zeros(self.years)
        
        self.netIncome = np.zeros(self.years)
        self.netCash = np.zeros(self.years)
        
        for i in range(self.iters):
            for j in range(self.years):
                self.totalTaxes[j] += fedTax[i,j] + ficaTax[i,j] + saltTaxes[i,j]
                self.totalDeducted[j] += ret.traditional.contribution[i,j] + healthDed[i,j]
                self.totalWithheld[j] += ret.roth.contribution[i,j] + healthBen[i,j]
                
                self.netIncome[j] += self.income[i,j] 
                self.netIncome[j] += self.tradWithdrawal[i,j] + self.rothWithdrawal[i,j] + ss.ssIns[i,j] if self.iters == self.numInd else np.sum(self.tradWithdrawal[:,j] + self.rothWithdrawal[:,j] + ss.ssIns[:,j])
        
        for j in range(self.years):
            self.netIncome[j] += np.sum([loan.prin if j == loan.loanYr else 0 for _,loan in loans.loanSummary.iterrows()])
            self.netIncome[j] -= self.totalTaxes[j]
            self.netCash[j] = self.netIncome[j] - self.totalDeducted[j] - self.totalWithheld[j]

    def savingsCalc(self):
        savings = self.vars.savings
        expenses = self.vars.expenses
        accounts = self.vars.accounts
        accountType = accounts.accountSummary.accountType
        
        # EXPENSES
        for exp,val in expenses.totalExpenses.items():
            self.expenses.loc[:,getattr(getattr(expenses,exp),'allocation')] += val
        
        # self.expenses.to_csv('Expenses.csv')

        # SAVINGS
        for j in range(self.years):
            for accName,_ in savings.earnings.items():
                match str(accountType.loc[accName]).upper():
                    case 'ROTH'|'TRAD':
                        pass
                    case _:
                        """PREVIOUS YEARS BALANCE"""
                        if j == 0:
                            self.savings.loc[0,accName] += accounts.accountSummary.baseSavings.loc[accName]
                        else:
                            self.savings.loc[j,accName] += self.savings.loc[j-1,accName]
                
                        """ADD ALLOCATIONS"""
                        self.savings.loc[j,accName] += savings.allocations.loc[j,accName] * self.netCash[j]

                        """SUBTRACT EXPENSES"""
                        self.savings.loc[j,accName] -= self.expenses.loc[j,accName]

                        """ADD EARNINGS"""
                        if j > 0:
                            self.savings.loc[j,accName] += savings.earnings.loc[j,accName] * self.savings.loc[j-1,accName]

                        if str(accountType.loc[accName]).upper() == '529':
                            if j > -max(self.childBaseAges) and self.isKids[j] == 0:
                                remainVal = self.savings.loc[j,accName]
                                self.savings.loc[j,accName] = 0
                                self.savings.loc[j,'savings'] += remainVal

        # self.savings.to_csv('Savings.csv')        

                # UNDERFLOW
                # for under in self.vars.accounts.underflow:
                #     if (len(under) == 3):
                #         if (j >= under[2][0]):
                #             self.withdrawal = self.underFlow(self.savings,j,under[0][0],under[1])
                #             self.savings = self.withdrawal.savings
                        
                #     else:
                #         self.withdrawal = self.underFlow(self.savings,j,under[0][0],under[1])
                #         self.savings = self.withdrawal.savings
                    
                # # OVERFLOW
                # for over in self.vars.accounts.overflow:
                #     if (len(over) == 4):
                #         if (j >= over[3]):
                #             self.withdrawal = self.overFlow(self.savings,j,over[0],over[1],over[2])
                #             self.savings = self.withdrawal.savings
                        
                #     else:
                #         self.withdrawal = self.overFlow(self.savings,j,over[0],over[1],over[2])
                #         self.savings = self.withdrawal.savings
                
                # Remove 529 Excess
                # if j > max(self.childBaseAges) and self.isKids[j] == 0:
                #     self.withdrawal = self.overFlow(self.savings,j,7,8,0) # College to Long-Term (Excess)
                #     self.savings = self.withdrawal.savings 
    
    # def overFlow(self, yr, maxVal, accFrom, accTo):
    #     accounts = self.vars.accounts

    #     overFlow = Withdrawal()
        
    #     index = accFrom
    #     amount = 0
    #     capGains = accounts.accountSummary.capGainsType[accFrom]
    #     savingsOut = savingsIn
        
    #     if self.savings[accFrom][yr] > maxVal:
    #         amount = savingsOut[accFrom][yr] - maxVal
    #         savingsOut[accFrom][yr] = maxVal
    #         savingsOut[accTo][yr] += amount

    #     overFlow.index = index
    #     overFlow.amount = amount
    #     overFlow.capGains = capGains
    #     overFlow.savings = savingsOut
        
    #     return overFlow
    
    # def underFlow(self, accIn, accOut):
        # underFlow = Withdrawal()
        
        # index = len(indFrom)
        # amount = len(indFrom)
        # capGains = len(indFrom)
        # savingsOut = savingsIn
        
        # if (savingsOut[indTo][yr] < 0):
        #     transferVal = -savingsOut[indTo][yr]
        #     savingsOut[indTo][yr] = 0
            
        #     accVal = len(indFrom)
        #     for i in range(len(indFrom)):
        #         accVal[i] = savingsOut[indFrom[i]][yr]
        #         if (accVal[i] < 0):
        #             accVal[i] = 0
            
        #     totalVal = np.sum(accVal)
            
        #     for i in range(len(indFrom)):
        #         index[i] = indFrom[i]
        #         capGains[i] = self.vars.accounts.capGainsType[i]
        #         if (totalVal == 0):
        #             amount[i] = transferVal / len(indFrom)
        #         else:
        #             amount[i] = (transferVal * (accVal[i] / totalVal))
                
        #         savingsOut[indFrom[i]][yr] -= amount[i]

        # underFlow.index = index
        # underFlow.amount = amount
        # underFlow.capGains = capGains
        # underFlow.savings = savingsOut
                
        # return underFlow