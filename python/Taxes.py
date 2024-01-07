import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

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
        self.summedInflation = vars.salary.summedInflation
        self.childInflation = vars.children.childInflation

        self.totalExpenses = vars.expenses.totalExpenses
        
        self.filingType = vars.filing.filingType.upper()
        self.filingState = vars.filing.filingState.upper()
        
        self.isKids = self.vars.children.isKids
        self.childBaseAges = self.vars.children.childBaseAges
        
    def run(self):
        savings = self.vars.savings

        self.expenses = pd.DataFrame(0,index=np.arange(self.years),columns=savings.earnings.columns)
        self.savings = pd.DataFrame(0,index=np.arange(self.years),columns=savings.earnings.columns)

#       Capital Gains
        ##############################
        self.stCapGains = np.zeros(self.years)
        self.ltCapGains = np.zeros(self.years)

#       Benefits
        ##############################
        self.healthCalc()
        
#       Retirement
        ##############################
        self.perc401 = np.zeros((self.numInd,self.years))
        self.cont401 = np.zeros((self.numInd,self.years))
        
        self.tradCont = self.retContCalc(self.vars.benefits.retirement.traditional)
        self.rothCont = self.retContCalc(self.vars.benefits.retirement.roth)
        self.matchCont = self.matchContCalc(self.vars.benefits.retirement.match)
        
        self.retirementWithdrawalCalc()

#       Deduction/Exemptions
        ##############################
        self.itemDedCalc()
        # plt.plot(self.itemDedFed[0])
        # plt.plot(self.itemDedState[0])
        
        self.stdDedCalc()
        # plt.plot(self.stdDedFed[0])

        self.exemptCalc()
        # plt.plot(self.persExemptState[0])

#       Gross Earnings
        ##############################
        self.grossEarnCalc()
        # plt.plot(self.taxableIncomeFed[0])
        # plt.plot(self.taxableIncomeState[0])

#       State Taxes
        ##############################
        self.slTaxCalc()
        # plt.plot(self.vars.taxes.state.saltTaxes[0])

        self.itemDedCalc()
        self.grossEarnCalc()
        # plt.plot(self.taxableIncomeFed[0])
        # plt.plot(self.taxableIncomeState[0])
        # plt.show()

#       Social Security
        ##############################
        self.ssTaxCalc()
        # plt.plot(self.ssTax)
        
#       Federal Taxes
        ##############################
        self.fedTaxCalc()
        # plt.plot(federal.fedTax[0])
        # plt.show()
        
#       Net income  
        ############################## 
        self.netIncCalc() 
        # plt.plot(taxes.netCash)
        # plt.show()

#       Savings
        ##############################
        self.savingsCalc()
        self.vars.taxes.savings = self.savings

        return self.vars
    
    def healthCalc(self):   
        health = self.vars.benefits.health              
        
        hsa = np.zeros((self.iters,self.years))
        fsa = np.zeros((self.iters,self.years))
        hra = np.zeros((self.iters,self.years))
        medicalPrem = np.zeros((self.iters,self.years))
        visionPrem  = np.zeros((self.iters,self.years))
        dentalPrem  = np.zeros((self.iters,self.years))

        self.healthDed = np.zeros((self.iters,self.years))
        self.healthBen = np.zeros((self.iters,self.years))  
        
        for i in range(self.iters):
            retire = min(self.retAges[i] - self.baseAges[i],self.years)
            for j in range(retire):
                """INFLATION"""
                hsa[i,j] = (health.hsa * self.summedInflation[j]) * (1 + self.childInflation[j])
                fsa[i,j] = (health.fsa * self.summedInflation[j]) * (1 + self.childInflation[j])
                hra[i,j] = (health.hra * self.summedInflation[j]) * (1 + self.childInflation[j])

                medicalPrem[i,j] = (health.medicalPrem * self.summedInflation[j]) * (1 + self.childInflation[j])
                visionPrem[i,j]  = (health.visionPrem * self.summedInflation[j]) * (1 + self.childInflation[j])
                dentalPrem[i,j]  = (health.dentalPrem * self.summedInflation[j]) * (1 + self.childInflation[j])

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
                maxCont = (retire.maxSelfCont + retire.maxCatchUpCont if self.vars.base.ages[i,j] >= retire.catchUpAge else retire.maxSelfCont) * self.summedInflation[j]
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
                maxCont = (retire.maxTotalCont + retire.maxCatchUpCont if self.vars.base.ages[i,j] >= retire.catchUpAge else retire.maxTotalCont) * self.summedInflation[j]
                if self.cont401[i,j] > maxCont:
                    contribution[i,j] -= self.cont401[i,j] - maxCont
        
        return contribution

    def ssTaxCalc(self):  
        ss = self.vars.benefits.socialSecurity

        match self.filingType:
            case "JOINT":    socialSecurity = self.taxes.federal.ss.joint
            case "SEPARATE": socialSecurity = self.taxes.federal.ss.separate
            case "SINGLE":   socialSecurity = self.taxes.federal.ss.single

        for j in range(self.years):
            ssIns = ss.ssIns[:,j] if self.iters == self.numInd else [np.sum(ss.ssIns[:,j])]

            for i in range(self.iters):
                for k in range(len(socialSecurity.bracketMax)):
                    if self.taxableIncomeFed[i,j] < socialSecurity.bracketMax[k]:
                        self.taxableBenefits[i,j] = socialSecurity.bracketPerc[k] * ssIns[i]

    def retirementWithdrawalCalc(self):
        def distributionYrs(age):
            return -0.00000684*age**4+0.00266293*age**3-0.37364604*age**2+21.78182*age-414.165
         
        savings = self.vars.savings
        accountSummary = self.vars.accounts.accountSummary
        ret = self.vars.benefits.retirement

        self.netTradCont = np.zeros(self.years)
        self.netRothCont = np.zeros(self.years)

        self.tradWithdrawal = np.zeros((self.numInd,self.years))
        self.rothWithdrawal = np.zeros((self.numInd,self.years))

        for j in range(self.years):
            for accName,_ in savings.earnings.items():
                """PREVIOUS YEARS BALANCE"""
                match str(accountSummary.accountType.loc[accName]).upper():
                    case 'ROTH'|'TRAD':
                        for i in range(self.numInd):
                            self.netTradCont[j] += self.tradCont[i,j] + self.matchCont[i,j]
                            self.netRothCont[j] += self.rothCont[i,j]
                            
                        if j == 0:
                            self.savings.loc[0,accName] += accountSummary.baseSavings.loc[accName]
                        else:
                            self.savings.loc[j,accName] += self.savings.loc[j-1,accName]
                
                """ADD CONTRIBUTIONS"""
                match str(accountSummary.accountType.loc[accName]).upper():
                    case 'ROTH': self.savings.loc[j,accName] += self.netRothCont[j]
                    case 'TRAD': self.savings.loc[j,accName] += self.netTradCont[j]

                """ADD EARNINGS"""
                match str(accountSummary.accountType.loc[accName]).upper():
                    case 'ROTH'|'TRAD':
                        if j > 0:
                            self.savings.loc[j,accName] += savings.earnings.loc[j,accName] * self.savings.loc[j-1,accName]

                """SUBTRACT DISTRIBTUIONS"""
                for i in range(self.numInd):
                    if self.ages[i,j] >= ret.rmdAge:
                        match str(accountSummary.accountType.loc[accName]).upper():
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

        mortInt = np.zeros((self.iters,self.years))
        charDon = np.zeros((self.iters,self.years))
        slpDed = np.zeros((self.iters,self.years))

        self.itemDedFed = np.zeros((self.iters,self.years))
        self.itemDedState = np.zeros((self.iters,self.years))
        self.saltTaxes = np.zeros((self.iters,self.years))

        for i in range(self.iters):
            for j in range(self.years):
                # FEDERAL
                # SLP Taxes
                slpDed[i,j] = (self.summedInflation[j] * itemDed.maxSalt) / self.iters if self.saltTaxes[i,j] > (self.summedInflation[j] * itemDed.maxSalt) / self.iters else self.saltTaxes[i,j]
                
                # Mortgage Interest
                if house.houseBal[j] < (self.summedInflation[j] * itemDed.maxHouse) / self.iters:
                    mortInt[i,j] = house.houseInt[j] / self.iters
                else:
                    mortInt[i,j] = ((house.houseInt[j] / house.houseBal[j]) * (self.summedInflation[j] * itemDed.maxHouse)) / self.iters
                
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
                self.stdDedFed[i,j] = ((self.summedInflation[j] * dedFed.maxFed) * self.numInd) / self.iters
                
                # STATE
                match self.filingState:
                    case "NJ": 
                        self.stdDedState[i,j] = 0                
                    case "MD":
                        dedState = self.taxes.state.md.deductions.standard

                        self.stdDedState[i,j] = dedState.basePerc * self.income[i,j]

                        if self.stdDedState[i,j] < (self.summedInflation[j] * dedState.stdDedMin) / self.iters:
                            self.stdDedState[i,j] = (self.summedInflation[j] * dedState.stdDedMin) / self.iters
                        elif self.stdDedState[i,j] > (self.summedInflation[j] * dedState.stdDedMax) / self.iters:
                            self.stdDedState[i,j] = (self.summedInflation[j] * dedState.stdDedMax) / self.iters
                    
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
                            if self.income[i,j] < (self.summedInflation[j] * persExempt.bracketMax[k]):
                                self.persExemptState[i,j] = (self.summedInflation[j] * persExempt.bracketAmt[k])                               
                                break
                        
                        for _ in range(int(self.isKids[j])):
                            for k in range(len(childExempt.bracketMax)):
                                if self.income[i,j] < (self.summedInflation[j] * childExempt.bracketMax[k]):
                                    self.childExemptState[i,j] += (self.summedInflation[j] * childExempt.bracketAmt[k]) / self.iters
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
                            if self.income[i,j] < (self.summedInflation[j] * persExempt.bracketMax[k]):
                                self.persExemptState[i,j] = (self.summedInflation[j] * persExempt.bracketAmt[k])
                                break
                        
                        for _ in range(int(self.isKids[j])):
                            for k in range(len(childExempt.bracketMax)):
                                if self.income[i,j] < (self.summedInflation[j] * childExempt.bracketMax[k]):
                                    self.childExemptState[i,j] += (self.summedInflation[j] * childExempt.bracketAmt[k]) / self.iters
                                    break
                    
                    case "AK"| "FL"| "NV"| "NH"| "SD"| "TN"| "TX"| "WA"| "WY":
                        self.persExemptState[i,j] = 0
                        self.childExemptState[i,j] = 0
    
    def grossEarnCalc(self):
        self.taxableIncomeFed = np.zeros((self.iters,self.years))
        self.taxableIncomeState = np.zeros((self.iters,self.years))
        self.taxableBenefits = np.zeros((self.iters,self.years))

        for i in range(self.iters):
            for j in range(self.years):
                # FEDERAL
                self.taxableIncomeFed[i,j] = self.income[i,j] + self.taxableBenefits[i,j] + self.tradWithdrawal[i,j] + (self.stCapGains[j] / self.iters)
                self.taxableIncomeFed[i,j] -= self.tradCont[i,j] + self.healthDed[i,j] + self.healthBen[i,j]
                self.taxableIncomeFed[i,j] -= self.itemDedFed[i,j] if self.itemDedFed[i,j] > self.stdDedFed[i,j] else self.stdDedFed[i,j]
                
                # STATE
                self.taxableIncomeState[i,j] = self.income[i,j]
                match self.filingState:
                    case "AK"| "FL"| "NV"| "NH"| "SD"| "TN"| "TX"| "WA"| "WY":
                        pass
                    case _:
                        self.taxableIncomeState[i,j] -= (self.tradCont[i,j] + self.persExemptState[i,j] + self.childExemptState[i,j])

                """HEALTH DEDUCTIONS"""
                match self.filingState:
                    case "AK"| "FL"| "NV"| "NH"| "SD"| "TN"| "TX"| "WA"| "WY"| "NJ"|"CA":
                        self.taxableIncomeState[i,j] -= self.healthDed[i,j]

                """RETIREMENT"""
                match self.filingState:
                    case "NJ":
                        self.taxableIncomeState[i,j] += self.tradWithdrawal[i,j]

                """SOCIAL SECURITY"""
                match self.filingState:
                    case "CO"| "CT"| "KS"| "MN"| "MO"| "MT"| "NE"| "NM"| "ND"| "RI"| "UT"| "VT"| "WV":
                        self.taxableIncomeState[i,j] += self.taxableBenefits[i,j]
                
                """CAPITAL GAINS"""
                match self.filingState:
                    case "AK"| "FL"| "NV"| "NH"| "SD"| "TN"| "TX"| "WA"| "WY":
                        pass
                    case _:
                        self.taxableIncomeState[i,j] += (self.stCapGains[j] + self.ltCapGains[j]) / self.iters
                
                self.taxableIncomeFed[i,j] = 0 if self.taxableIncomeFed[i,j] < 0 else self.taxableIncomeFed[i,j]
                self.taxableIncomeState[i,j] = 0 if self.taxableIncomeState[i,j] < 0 else self.taxableIncomeState[i,j]
    
    def slTaxCalc(self):
        house = self.vars.expenses.house
        
        stateTax = np.zeros((self.iters,self.years))
        localTax = np.zeros((self.iters,self.years))
        propTax = np.zeros((self.iters,self.years))
        
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
                    maxBracket = (self.summedInflation[j] * state.bracketMax[k])
                    rateBracket = state.bracketPerc[k]
                    
                    if self.taxableIncomeState[i,j] > maxBracket:
                        stateTax[i,j] += (maxBracket - minBracket) * rateBracket
                    elif self.taxableIncomeState[i,j] > minBracket:
                        stateTax[i,j] += (self.taxableIncomeState[i,j] - minBracket) * rateBracket

                
                localTax[i,j] = self.taxableIncomeState[i,j] * local.localPerc
                propTax[i,j] = house.houseWth[j] * house.propTax
                
                self.saltTaxes[i,j] += stateTax[i,j] + localTax[i,j] + propTax[i,j]
    
    def fedTaxCalc(self):      
        self.fedTax = np.zeros((self.iters,self.years))
        self.ficaTax = np.zeros((self.iters,self.years))
        self.capGainsTax = np.zeros((self.iters,self.years))

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
                    maxBracket = (self.summedInflation[j] * federal.bracketMax[k])
                    rateBracket = federal.bracketPerc[k]
                    
                    if self.taxableIncomeFed[i,j] > maxBracket:
                        self.fedTax[i,j] += (maxBracket - minBracket) * rateBracket
                    elif (self.taxableIncomeFed[i,j] > minBracket):
                        self.fedTax[i,j] += (self.taxableIncomeFed[i,j] - minBracket) * rateBracket
                
                # SS Tax
                if self.taxableIncomeFed[i,j] < (self.summedInflation[j] * socialSecurity.maxSal):
                    self.ficaTax[i,j] += self.taxableIncomeFed[i,j] * socialSecurity.rate
                else:
                    self.ficaTax[i,j] += (self.summedInflation[j] * socialSecurity.maxSal) * socialSecurity.rate
                
                # Medicare Tax
                if self.taxableIncomeFed[i,j] < (self.summedInflation[j] * medicare.maxSal):
                    self.ficaTax[i,j] += self.taxableIncomeFed[i,j] * medicare.rate
                else:
                    self.ficaTax[i,j] += (self.summedInflation[j] * medicare.maxSal) * medicare.rate
                    self.ficaTax[i,j] += (self.taxableIncomeFed[i,j] - (self.summedInflation[j] * medicare.maxSal)) * medicare.addRate
    
    def capGainsTaxCalc(self):
        capitalGains = self.taxes.federal.capitalGains

        taxableGains = np.zeros((self.iters,self.years))

        match self.filingType:
            case "JOINT":    capGains = capitalGains.joint
            case "SEPARATE": capGains = capitalGains.separate
            case "SINGLE":   capGains = capitalGains.single        

        for j in range(self.years):
            for i in range(self.iters):
                for k in range(len(capGains.bracketMax)):
                    if self.taxableIncomeFed[i,j] < capGains.bracketMax[k]:
                        taxableGains[i,j] = capGains.bracketPerc[k] * (self.ltCapGains[j] / self.iters)

        """TAX"""
        self.capGainsTax
    
    def netIncCalc(self):
        loans = self.vars.expenses.loans
        ss = self.vars.benefits.socialSecurity

        self.totalTaxes = np.zeros(self.years)
        self.totalDeducted = np.zeros(self.years)
        self.totalWithheld = np.zeros(self.years)
        
        self.netIncome = np.zeros(self.years)
        self.netCash = np.zeros(self.years)

        self.taxRate = np.zeros(self.years)
        
        for i in range(self.iters):
            for j in range(self.years):
                self.totalTaxes[j]    += self.fedTax[i,j] + self.ficaTax[i,j] + self.saltTaxes[i,j] + self.capGainsTax[i,j]
                self.totalDeducted[j] += self.tradCont[i,j] + self.healthDed[i,j]
                self.totalWithheld[j] += self.rothCont[i,j] + self.healthBen[i,j]
                
                self.netIncome[j] += self.income[i,j]
            
        for j in range(self.years):
            self.netIncome[j] += np.sum(self.tradWithdrawal[:,j] + self.rothWithdrawal[:,j] + ss.ssIns[:,j])
            self.netIncome[j] += np.sum([loan.prin if j == loan.loanYr else 0 for _,loan in loans.loanSummary.iterrows()])
            self.netIncome[j] += self.stCapGains[j] + self.ltCapGains[j]
            
            self.taxRate[j] = self.totalTaxes[j] / self.netIncome[j]

            self.netIncome[j] -= self.totalTaxes[j]
            self.netCash[j]    = self.netIncome[j] - self.totalDeducted[j] - self.totalWithheld[j]

    def savingsCalc(self):   
        def getWithdrawal(reqWithdrawal):
            withdrawal = min(reqWithdrawal,max(0,self.savings.loc[j,accFrom]))
            capGains = accountSummary.capGainsType.loc[accFrom].upper()

            reqWithdrawal -= withdrawal
            self.savings.loc[j,accFrom] -= withdrawal
            
            match capGains:
                case 'SHORT':
                    self.stCapGains[j] += withdrawal
                case 'LONG':
                    self.ltCapGains[j] += withdrawal
            
            return reqWithdrawal

        def underFlowOrder():
            accsTo = []
            accsFrom = []
            for accName,_ in savings.earnings.items():
                if not pd.isna(accountSummary.underflow.loc[accName]):
                    accsFrom.append(accountSummary.underflow.loc[accName])
                    accsTo.append(accName)

            for accTo in accsTo:
                if accTo not in accsFrom:
                    acc = accTo

            order = []
            while True:
                order.append(acc)
                acc = accountSummary.underflow.loc[acc]

                if pd.isna(acc):
                    order.pop()
                    break

            return order

        def overFlow(yr, account, accountTo, capGainsType, maxBal=1e9):
            capGainsType = self.vars.accounts.accountSummary.capGainsType

            if self.savings.loc[yr,account] > maxBal:
                diff = self.savings.loc[yr,account] - maxBal
                self.savings.loc[yr,account] = maxBal
                self.savings.loc[yr,accountTo] += diff

                capGains = capGainsType.loc[account].upper()

                match capGains:
                    case 'SHORT':
                        self.stCapGains[j] += diff
                    case 'LONG':
                        self.ltCapGains[j] += diff

        def calculateTaxes():
            self.grossEarnCalc()

            self.slTaxCalc()
            self.itemDedCalc()

            self.grossEarnCalc()

            self.ssTaxCalc()
            self.capGainsTaxCalc()
            self.fedTaxCalc()

            self.netIncCalc()

        savings = self.vars.savings
        expenses = self.vars.expenses
        accountSummary = self.vars.accounts.accountSummary
        
        # EXPENSES
        for exp,val in expenses.totalExpenses.items():
            self.expenses.loc[:,getattr(getattr(expenses,exp),'allocation')] += val
        
        # self.expenses.to_csv('Expenses.csv')

        # SAVINGS
        for j in range(self.years):
            ######################################################################################
            """EXPENSES"""
            for accName,_ in savings.earnings.items():
                match str(accountSummary.accountType.loc[accName]).upper():
                    case 'ROTH'|'TRAD': pass
                    case _:
                        """PREVIOUS YEARS BALANCE"""
                        if j == 0:
                            self.savings.loc[0,accName] += accountSummary.baseSavings.loc[accName]
                        else:
                            self.savings.loc[j,accName] += self.savings.loc[j-1,accName]

                        """SUBTRACT EXPENSES"""
                        self.savings.loc[j,accName] -= self.expenses.loc[j,accName]

            ######################################################################################
            """WITHDRAWALS"""
            rebalance = 0
            for accName,_ in savings.earnings.items():
                match str(accountSummary.accountType.loc[accName]).upper():
                    case 'ROTH'|'TRAD': pass
                    case _: rebalance += abs(self.savings.loc[j,accName]) if self.savings.loc[j,accName] < 0 else 0

            """WITHDRAWAL AND TAX"""
            # self.netCash[j] = 25e3
            # rebalance = 30e3
            if rebalance > self.netCash[j]:
                """GET WITHDRAWALS"""
                reqWithdrawal = (rebalance - self.netCash[j]) * (1 + self.taxRate[j] + 0.05) # Including 5% margin for additional taxes
                withdrawalOrder = underFlowOrder()

                accFrom = withdrawalOrder[0]
                reqWithdrawal = getWithdrawal(reqWithdrawal)

                for accName in withdrawalOrder:
                    accFrom = accountSummary.underflow.loc[accName]
                    if not pd.isna(accFrom):
                        reqWithdrawal = getWithdrawal(reqWithdrawal)
                    
                        if reqWithdrawal <= 0:
                            break
                
                # if reqWithdrawal > 0:
                #     print('--------------------')
                #     print("YEAR - ",str(j)," - Net expenses.. ",str(np.sum(self.expenses.loc[j,:])))
                #     print("YEAR - ",str(j)," - Net savings... ",str(np.sum(self.savings.loc[j,:])+self.netCash[j]))

                """TAX WITHDRAWALS"""
                calculateTaxes()

            """REFILL NEGATIVE ACCOUNTS"""
            netCash = self.netCash[j]
            for accName,_ in savings.earnings.items():
                match str(accountSummary.accountType.loc[accName]).upper():
                    case 'ROTH'|'TRAD': pass
                    case _:
                        if self.savings.loc[j,accName] < 0 and netCash > 0:
                            deposit = min(abs(self.savings.loc[j,accName]),netCash)
                            netCash -= deposit
                            self.savings.loc[j,accName] += deposit

            ######################################################################################
            """ALLOCATIONS & EARNINGS"""
            for accName,_ in savings.earnings.items():
                match str(accountSummary.accountType.loc[accName]).upper():
                    case 'ROTH'|'TRAD': pass
                    case _:
                        """ADD ALLOCATIONS"""
                        self.savings.loc[j,accName] += savings.allocations.loc[j,accName] * netCash

                        """ADD EARNINGS"""
                        if j > 0:
                            if self.savings.loc[j-1,accName] > 0:
                                self.savings.loc[j,accName] += savings.earnings.loc[j,accName] * self.savings.loc[j-1,accName]

                        if str(accountSummary.accountType.loc[accName]).upper() == '529':
                            if any(self.isKids):
                                if j > -max(self.childBaseAges) and self.isKids[j] == 0:
                                    remainVal = self.savings.loc[j,accName]
                                    self.savings.loc[j,accName] = 0
                                    self.savings.loc[j,'savings'] += remainVal

                        """ADJUST UNDERFLOW/OVERFLOW"""
                        if not pd.isna(accountSummary.overflow.loc[accName]):
                            overFlow(j, 
                                     accName,
                                     accountSummary.overflow.loc[accName],
                                     accountSummary.capGainsType.loc[accountSummary.overflow.loc[accName]],
                                     maxBal=accountSummary.overAmt.loc[accName] if not pd.isna(accountSummary.overAmt.loc[accName]) else 1e9)

                        """TAX WITHDRAWALS"""
                        calculateTaxes()