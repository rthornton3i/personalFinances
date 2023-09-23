from Utility import Utility

import numpy as np
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

        self.income = vars.salary.income
        self.salary = vars.salary.salary
        self.inflation = vars.salary.inflation
        self.childInflation = vars.children.childInflation
        
        self.ssIns = vars.benefits.socialSecurity.ssIns
        self.expenses = vars.expenses.totalExpenses
        
        self.filingType = vars.filing.filingType.upper()
        self.filingState = [f.upper() for f in vars.filing.filingState]
        
        self.childAges = vars.children.childAges
        self.maxChildYr = vars.children.maxChildYr
        
    def run(self):          
#      Benefits
        self.healthCalc()
        self.vars.benefits.health.healthDed = self.healthDed
        self.vars.benefits.health.healthBen = self.healthBen
        
#      Retirement
        self.perc401 = np.zeros((self.numInd,self.years))
        self.cont401 = np.zeros((self.numInd,self.years))
        
        self.vars.benefits.retirement.traditional.contribution = self.retContCalc(self.vars.benefits.retirement.traditional)
        self.vars.benefits.retirement.roth.contribution = self.retContCalc(self.vars.benefits.retirement.roth)
        self.vars.benefits.retirement.match.contribution = self.matchContCalc(self.vars.benefits.retirement.match)
        
        # self.vars.benefits.retirement.traditional.withdrawal = self.retirementWithdrawals()
        # self.vars.benefits.retirement.roth.withdrawal = self.retirementWithdrawals()

#      Social Security
        self.ssTaxCalc()
        self.vars.benefits.socialSecurity.ssTax = self.ssTax
        # plt.plot(self.ssTax)

#      Deduction/Exemptions
        self.itemDedCalc()
        self.vars.taxes.federal.deductions.itemized.itemDedFed = self.itemDedFed
        self.vars.taxes.state.deductions.itemized.itemDedState = self.itemDedState
        # plt.plot(self.itemDedFed[0])
        # plt.plot(self.itemDedState[0])
        
        self.stdDedCalc()
        self.vars.taxes.federal.deductions.standard.stdDedFed = self.stdDedFed
        self.vars.taxes.state.deductions.standard.stdDedState = self.stdDedState
        # plt.plot(self.stdDedFed[0])

        self.exemptCalc()
        self.vars.taxes.federal.exemptions.exemptFed = self.exemptFed
        self.vars.taxes.state.exemptions.persExempt.persExemptState = self.persExemptState
        self.vars.taxes.state.exemptions.childExempt.childExemptState = self.childExemptState
        # plt.plot(self.persExemptState[0])

#      Gross Earnings
        self.grossEarnCalc()
        self.vars.taxes.federal.grossIncomeFed = self.grossIncomeFed
        self.vars.taxes.state.grossIncomeState = self.grossIncomeState
        plt.plot(self.grossIncomeFed[0])
        plt.plot(self.grossIncomeState[0])

#      State Taxes
        self.vars.taxes.state.saltTaxes = self.slTaxCalc()
        
#      Gross Earnings (Update)
        self.itemDedCalc()
        self.vars.taxes.federal.deductions.itemized.itemDedFed = self.itemDedFed
        self.vars.taxes.state.deductions.itemized.itemDedState = self.itemDedState
        
        self.grossEarnCalc()
        self.vars.taxes.federal.grossIncomeFed = self.grossIncomeFed
        self.vars.taxes.state.grossIncomeState = self.grossIncomeState
        
#      Federal Taxes
        [self.vars.taxes.federal.fedTax, \
        self.vars.taxes.federal.ficaTax] = self.fedTaxCalc()
        
#      Net self.income                         
        [self.vars.taxes.totalTaxes, \
        self.vars.taxes.totalDeducted, \
        self.vars.taxes.totalWithheld, \
        \
        self.vars.taxes.netIncome, \
        self.vars.taxes.netCash, \
        self.vars.benefits.retirement.netTradCont, \
        self.vars.benefits.retirement.netRothCont] = self.netIncCalc()

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
            retire = self.retAges[i] - self.baseAges[i]
            hsaExp = health.hsa
            fsaExp = health.fsa
            hraExp = health.hra
            
            medicalPremExp = health.medicalPrem
            visionPremExp  = health.visionPrem
            dentalPremExp  = health.dentalPrem

            for j in range(retire):
                """INFLATION"""
                hsaExp *= 1 + self.inflation[j] 
                fsaExp *= 1 + self.inflation[j] 
                hraExp *= 1 + self.inflation[j] 

                medicalPremExp *= 1 + self.inflation[j] 
                visionPremExp  *= 1 + self.inflation[j] 
                dentalPremExp  *= 1 + self.inflation[j]

                hsa[i,j] = hsaExp * (1 + self.childInflation[j])
                fsa[i,j] = fsaExp * (1 + self.childInflation[j])
                hra[i,j] = hraExp * (1 + self.childInflation[j])

                medicalPrem[i,j] = medicalPremExp * (1 + self.childInflation[j])
                visionPrem[i,j]  = visionPremExp * (1 + self.childInflation[j])
                dentalPrem[i,j]  = dentalPremExp * (1 + self.childInflation[j])

        # Post-retirement

        self.healthDed  = np.sum((hsa,fsa,hra),0)
        self.healthBen  = np.sum((medicalPrem,visionPrem,dentalPrem),0)
    
    def retContCalc(self,retirement):        
        retire = self.vars.benefits.retirement

        ret401Perc = np.zeros((self.numInd,self.years))
        
        for i in range(self.numInd):
            for j in range(self.years):
                ret401Perc[i,j] = retirement.basePerc
        
        contribution =  np.multiply(ret401Perc,self.salary)
        self.perc401 = np.sum((self.perc401,ret401Perc),0)
        self.cont401 = np.sum((self.cont401,contribution),0)

        for i in range(self.numInd):
            for j in range(self.years):
                maxCont = retire.maxSelfCont + retire.maxCatchUpCont if self.vars.base.ages[i,j] >= retire.catchUpAge else retire.maxSelfCont
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
                maxCont = retire.maxTotalCont + retire.maxCatchUpCont if self.vars.base.ages[i,j] >= retire.catchUpAge else retire.maxTotalCont
                if self.cont401[i,j] > maxCont:
                    contribution[i,j] -= self.cont401[i,j] - maxCont
        
        return contribution

    def ssTaxCalc(self):  
        # TODO: NEEDS UPDATE    
        self.taxableBenefits = np.zeros((self.iters,self.years))
        self.ssTax = np.zeros((self.iters,self.years))

        match self.filingType:
            case "JOINT":    socialSecurity = self.taxes.federal.ss.joint
            case "SEPARATE": socialSecurity = self.taxes.federal.ss.separate
            case "SINGLE":   socialSecurity = self.taxes.federal.ss.single
            case _:          socialSecurity = self.taxes.federal.ss.single # Assume Single 
         
        # for i in range(self.iters):
        #     for j in range(self.years):
        #         combinedIncome = self.salary[i,j] + (self.ssIns[i,j] / 2)
        #         for k in range(len(socialSecurity.bracketMax)):
        #             if combinedIncome < socialSecurity.bracketMax[k]:
        #                 self.taxableBenefits[i,j] = socialSecurity.bracketPerc[k] * self.ssIns[i,j]

    
    def itemDedCalc(self):
        itemDed = self.taxes.federal.deductions.itemized
        house = self.vars.expenses.housing.house
        charity = self.vars.expenses.charity
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
                    slpDed[i,j] = itemDed.maxSlp / self.iters if saltTaxes[i,j] > itemDed.maxSlp / self.iters else saltTaxes[i,j]
                else:
                    slpDed[i,j] = 0
                
                # Mortgage Interest
                if house.houseBal[j] < itemDed.maxHouse / self.iters:
                    mortInt[i,j] = house.houseInt[j] / self.iters
                else:
                    mortInt[i,j] = ((house.houseInt[j] / house.houseBal[j]) * itemDed.maxHouse) / self.iters
                
                # Charitable Donations
                charDon[i,j] = charity.total[j] / self.iters
                
                self.itemDedFed[i,j] = slpDed[i,j] + mortInt[i,j] + charDon[i,j]
                
                # STATE
                match self.filingState[i]:
                    case "NJ": self.itemDedState[i,j] = 0
                    case "MD": self.itemDedState[i,j] = 0
    
    def stdDedCalc(self):
        dedFed = self.taxes.federal.deductions.standard

        self.stdDedFed = np.zeros((self.iters,self.years))
        self.stdDedState = np.zeros((self.iters,self.years))
                
        for i in range(self.iters):
            for j in range(self.years):
                # FEDERAL
                self.stdDedFed[i,j] = (dedFed.maxFed * self.numInd) / self.iters
                
                # STATE
                match self.filingState[i]:
                    case "NJ": 
                        self.stdDedState[i,j] = 0                
                    case "MD":
                        dedState = self.taxes.state.md.deductions.standard

                        self.stdDedState[i,j] = dedState.basePerc * self.income[i][j]

                        if self.stdDedState[i,j] < dedState.stdDedMin / self.iters:
                            self.stdDedState[i,j] = dedState.stdDedMin / self.iters
                        elif self.stdDedState[i,j] > dedState.stdDedMax / self.iters:
                            self.stdDedState[i,j] = dedState.stdDedMax / self.iters
                    
                    case "AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY":
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
                match self.filingState[i]:
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
                            if self.income[i][j] < persExempt.bracketMax[k]:
                                self.persExemptState[i,j] = persExempt.bracketAmt[k]                                
                                break
                        
                        for childAge in self.childAges:
                            if childAge[j] > 0 and childAge[j] <= self.maxChildYr:
                                for k in range(len(childExempt.bracketMax)):
                                    if self.income[i][j] < childExempt.bracketMax[k]:
                                        self.childExemptState[i,j] += childExempt.bracketAmt[k] / self.iters
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
                            if self.income[i][j] < persExempt.bracketMax[k]:
                                self.persExemptState[i,j] = persExempt.bracketAmt[k]
                                break
                        
                        for childAge in self.childAges:
                            if childAge[j] > 0 and childAge[j] <= self.maxChildYr:
                                for k in range(len(childExempt.bracketMax)):
                                    if self.income[i][j] < childExempt.bracketMax[k]:
                                        self.childExemptState[i,j] += childExempt.bracketAmt[k] / self.iters
                                        break
                    
                    case "AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY":
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
                self.grossIncomeFed[i,j] = self.income[i][j] + self.taxableBenefits[i,j] - (contribution[i,j] + healthDed[i,j] + healthBen[i,j])
                self.grossIncomeFed[i,j] -= itemDedFed[i,j] if itemDedFed[i,j] > stdDedFed[i,j] else stdDedFed[i,j]
                
                # STATE
                match self.filingState[i]:
                    case "NJ","CA":
                        self.grossIncomeState[i,j] = self.income[i][j] - (contribution[i,j] + persExemptState[i,j] + childExemptState[i,j])
                    case "AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY":
                        self.grossIncomeState[i,j] = self.income[i][j]
                    case _:
                        self.grossIncomeState[i,j] = self.income[i][j] - (contribution[i,j] + persExemptState[i,j] + childExemptState[i,j] + healthDed[i,j])

                match self.filingState[i]:
                    case "CO", "CT", "KS", "MN", "MO", "MT", "NE", "NM", "ND", "RI", "UT", "VT", "WV":
                        self.grossIncomeState[i,j] += self.taxableBenefits[i,j]
                
                match self.filingState[i]:
                    case "AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY":
                        pass
                    case _:
                        self.grossIncomeState[i,j] -= itemDedState[i,j] if itemDedState[i,j] > stdDedState[i,j] else stdDedState[i,j]
    
    def slTaxCalc(self):
        house = self.vars.expenses.housing.house
        
        stateTax = np.zeros((self.iters,self.years))
        localTax = np.zeros((self.iters,self.years))
        propTax = np.zeros((self.iters,self.years))

        saltTaxes = np.zeros((self.iters,self.years))

        grossIncomeState = self.vars.taxes.state.grossIncomeState
        
        for i in range(self.iters):
            match self.filingState[i]:
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
                        case _:          state = self.taxes.state.md.state.single # Assume Single

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
                    maxBracket = state.bracketMax[k]
                    rateBracket = state.bracketPerc[k]
                    
                    if grossIncomeState[i,j] > maxBracket:
                        stateTax[i,j] += (maxBracket - minBracket) * rateBracket
                    elif grossIncomeState[i,j] > minBracket:
                        stateTax[i,j] += (grossIncomeState[i,j] - minBracket) * rateBracket

                
                localTax[i,j] = grossIncomeState[i,j] * local.localPerc
                propTax[i,j] = house.houseWth[j] * house.propTax
                
                saltTaxes[i,j] += stateTax[i,j] + localTax[i,j] + propTax[i,j]

        return saltTaxes
    
    def fedTaxCalc(self):    
        fedTax = np.zeros((self.iters,self.years))
        ficaTax = np.zeros((self.iters,self.years))

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
                    maxBracket = federal.bracketMax[k]
                    rateBracket = federal.bracketPerc[k]
                    
                    if grossIncomeFed[i,j] > maxBracket:
                        fedTax[i,j] += (maxBracket - minBracket) * rateBracket
                    elif (grossIncomeFed[i,j] > minBracket):
                        fedTax[i,j] += (grossIncomeFed[i,j] - minBracket) * rateBracket
                
                # SS Tax
                if grossIncomeFed[i,j] < socialSecurity.maxSal:
                    ficaTax[i,j] += grossIncomeFed[i,j] * socialSecurity.rate
                else:
                    ficaTax[i,j] += socialSecurity.maxSal * socialSecurity.rate
                
                # Medicare Tax
                if grossIncomeFed[i,j] < medicare.maxSal:
                    ficaTax[i,j] += grossIncomeFed[i,j] * medicare.rate
                else:
                    ficaTax[i,j] += medicare.maxSal * medicare.rate
                    ficaTax[i,j] += (grossIncomeFed[i,j] - medicare.maxSal) * medicare.addRate

        return fedTax, ficaTax
    
    def netIncCalc(self):
        ret = self.vars.benefits.retirement

        fedTax = self.vars.taxes.federal.fedTax
        ficaTax = self.vars.taxes.federal.ficaTax
        saltTaxes = self.vars.taxes.state.saltTaxes

        healthDed = self.vars.benefits.health.healthDed
        healthBen = self.vars.benefits.health.healthBen

        totalTaxes = np.zeros(self.years)
        totalDeducted = np.zeros(self.years)
        totalWithheld = np.zeros(self.years)
        
        netIncome = np.zeros(self.years)
        netCash = np.zeros(self.years)
        netTradCont = np.zeros(self.years)
        netRothCont = np.zeros(self.years)
        
        for i in range(self.iters):
            for j in range(self.years):
                totalTaxes[j] += fedTax[i,j] + ficaTax[i,j] + saltTaxes[i,j]
                totalDeducted[j] += ret.traditional.contribution[i,j] + healthDed[i,j]
                totalWithheld[j] += ret.roth.contribution[i,j] + healthBen[i,j]
                
                netIncome[j] += self.income[i][j]
                netTradCont[j] += ret.traditional.contribution[i,j] + ret.match.contribution[i,j]
                netRothCont[j] += ret.roth.contribution[i,j]
        
        for j in range(self.years):
            netIncome[j] -= totalTaxes[j]
            netCash[j] = netIncome[j] - totalDeducted[j] - totalWithheld[j]

        return totalTaxes, totalDeducted, totalWithheld, netIncome, netCash, netTradCont, netRothCont