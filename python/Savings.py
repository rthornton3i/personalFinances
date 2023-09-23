from Utility import Utility

import numpy as np
import pandas as pd
import math

class Savings:

    def __init__(self,vars):
        self.vars = vars
        
        self.years = vars.base.years
        self.numInd = vars.base.numInd
        
        self.netCash = vars.taxes.netCash
        self.numAccounts = len(vars.accounts.__dict__.items())
        # self.accountName = vars.accounts.accountName
    
    def run(self):
        self.savings = np.zeros((self.numAccounts,self.years))
        self.contributions = np.zeros((self.numAccounts,self.years))
        self.withdrawals = np.zeros((self.numAccounts,self.years))
        
        self.allocCalc()
        self.vars.savings.allocations = self.allocations

        self.earningCalc()
        self.vars.savings.earnings = self.earnings
        
        self.savingsCalc()
        self.vars.savings.allocations = self.allocations
        self.vars.savings.earnings = self.earnings
        self.vars.savings.contributions = self.contributions
        self.vars.savings.savings = self.savings
        self.vars.savings.withdrawals = self.withdrawals
        
        return self.vars
    
    
    def allocCalc(self):
        accounts = self.vars.accounts

        tempAllocations = accounts.allocations.copy()

        maxAllocation = tempAllocations.max(axis=None)
        binWidth = int(self.years / (tempAllocations.shape[1] - 1))
        
        self.allocations = pd.DataFrame(columns=np.arange(self.years))
        for _, acc in tempAllocations.iterrows():
            self.allocations.loc[acc.name] = np.interp(np.arange(self.years),np.arange(0,self.years+1,binWidth),acc.values) / maxAllocation
    
    def earningCalc(self):
        accounts = self.vars.accounts

        tempEarnings = accounts.earnings.copy()
        
        self.earnings = pd.DataFrame(columns=np.arange(self.years))
        values = []
        for _, acc in tempEarnings.iterrows():
            if any(np.isnan(acc.values)):
                values = np.random.normal(acc.values[0],acc.values[1],self.years)
            else:
                mu    = np.interp(np.arange(self.years),[0,self.years],[acc.values[0],acc.values[2]])
                sigma = np.interp(np.arange(self.years),[0,self.years],[acc.values[1],acc.values[3]])
                
                values = [np.random.normal(mu[j],sigma[j]) for j in range(self.years)]
            
            if accounts.accountSummary.loc[acc.name].accountType == 'SAVINGS':
                values = [0 if v < 0 else v for v in values]

            self.earnings.loc[acc.name] = values 
    
    def savingsCalc(self):
        accounts = self.vars.accounts
        ret = self.vars.benefits.retirement
        exps = self.vars.expenses
        house = self.vars.expenses.housing.house
        cars = self.vars.expenses.cars
        
        expenses = np.zeros(self.numAccounts)
                       
        for j in range(self.years):
            # Retirement RMD
            rmd = 0
            avgAge = 0
            for i in range(self.numInd):
                avgAge += self.vars.base.ages[i,j]
                if (j >= ret.rmdAge - self.vars.base.baseAges[i]):
                    rmd += self.vars.salary.salBase[i] / np.sum(self.vars.salary.salBase)

            avgAge /= self.numInd
            
            # EXPENSES
            for _, acc in accounts.earnings.iterrows():
                match (acc.name.upper()):
                    case 'COLLEGE529':
                        expenses[i] = exps.education.total[j]
                    
                    case "LONGTERMSAVINGS":
                        expenses[i] = house.houseDwn[j] + cars.carDwn[j] + exps.major.total[j]  
                    
                    case "SHORTTERMSAVINGS":
                        expenses[i] = exps.vacation.total[j] + exps.charity.total[j] + exps.random.total[j]  
                    
                    case "SPENDING":
                        expenses[i] = exps.housing.rent.total[j] + exps.housing.house.total[j] + exps.cars.total[j] + \
                                      exps.food.total[j] + exps.entertain.total[j] + exps.personalCare.total[j] + \
                                      exps.healthcare.total[j] + exps.pet.total[j] + exps.holiday.total[j]  
            
            # CONTRIBUTIONS
            totalExpenses = np.sum(expenses)
            if (totalExpenses > self.netCash[j]):
                netCont = self.netCash[j]
            else:
                netCont = totalExpenses
            
            remCash = self.netCash[j] - netCont
            
            # SAVINGS
            for i in range(self.numAccounts):                
                # CONTRIBUTIONS
                if (j == 0):
                    self.savings[i,j] += self.vars.accounts.baseSavings[i]
                else:
                    self.savings[i,j] += self.savings[i][j-1]

                self.contributions[i,j] += ((expenses[i] / totalExpenses) * netCont)
                self.contributions[i,j] += (self.allocations[i,j] * remCash)
                self.savings[i,j] += self.contributions[i,j]
                
                # EXPENSES
                self.savings[i,j] -= expenses[i]
                rmdDist = 0
                match (self.accountName[i].upper()):
                    case "ROTH 401K", "TRADITIONAL 401K":
                        if (rmd > 0):
                            accValue = (self.savings[i,j] * rmd)
                            ageFactor = avgAge * math.pow(ret.rmdFactor[0],2) + avgAge * ret.rmdFactor[1] + ret.rmdFactor[2]
                            rmdDist = (accValue / ageFactor)
                        
                match (self.accountName[i].upper()):
                    case "ROTH 401K": # ROTH 401k
                        self.savings[i,j] += ret.netRothCont[j]
                        self.savings[i,j] -= rmdDist
                    
                    case "TRADITIONAL 401K": # TRAD 401k                        
                        self.savings[i,j] += ret.netTradCont[j]
                        self.savings[i,j] -= rmdDist

                # EARNINGS
                if (self.savings[i,j] > 0):
                    self.savings[i,j] *= 1 + self.earnings[i,j]
                
            # UNDERFLOW
            for under in self.vars.accounts.underflow:
                if (len(under) == 3):
                    if (j >= under[2][0]):
                        self.withdrawal = self.underFlow(self.savings,j,under[0][0],under[1])
                        self.savings = self.withdrawal.savings
                    
                else:
                    self.withdrawal = self.underFlow(self.savings,j,under[0][0],under[1])
                    self.savings = self.withdrawal.savings
                
            # OVERFLOW
            for over in self.vars.accounts.overflow:
                if (len(over) == 4):
                    if (j >= over[3]):
                        self.withdrawal = self.overFlow(self.savings,j,over[0],over[1],over[2])
                        self.savings = self.withdrawal.savings
                    
                else:
                    self.withdrawal = self.overFlow(self.savings,j,over[0],over[1],over[2])
                    self.savings = self.withdrawal.savings
            
            childMax = False
            for i in range(len(self.vars.children.childAges)):
                if (self.vars.children.childAges[i,j] > self.vars.children.maxChildYr):
                    childMax = True

            if (childMax):
                self.withdrawal = self.overFlow(self.savings,j,7,8,0) # College to Long-Term (Excess)
                self.savings = self.withdrawal.savings 
    
    def overFlow(self,savingsIn, yr, indFrom, indTo, maxVal):
        overFlow = Withdrawal()
        
        index = indFrom
        amount = 0
        capGains = self.vars.accounts.capGainsType[indFrom]
        savingsOut = savingsIn
        
        if (savingsOut[indFrom][yr] > maxVal):
            amount = savingsOut[indFrom][yr] - maxVal
            savingsOut[indFrom][yr] = maxVal
            savingsOut[indTo][yr] += amount

        overFlow.index = index
        overFlow.amount = amount
        overFlow.capGains = capGains
        overFlow.savings = savingsOut
        
        return overFlow
    
    
    def underFlow(self,savingsIn, yr, indTo, indFrom):
        underFlow = Withdrawal()
        
        index = len(indFrom)
        amount = len(indFrom)
        capGains = len(indFrom)
        savingsOut = savingsIn
        
        if (savingsOut[indTo][yr] < 0):
            transferVal = -savingsOut[indTo][yr]
            savingsOut[indTo][yr] = 0
            
            accVal = len(indFrom)
            for i in range(len(indFrom)):
                accVal[i] = savingsOut[indFrom[i]][yr]
                if (accVal[i] < 0):
                    accVal[i] = 0
            
            totalVal = np.sum(accVal)
            
            for i in range(len(indFrom)):
                index[i] = indFrom[i]
                capGains[i] = self.vars.accounts.capGainsType[i]
                if (totalVal == 0):
                    amount[i] = transferVal / len(indFrom)
                else:
                    amount[i] = (transferVal * (accVal[i] / totalVal))
                
                savingsOut[indFrom[i]][yr] -= amount[i]

        underFlow.index = index
        underFlow.amount = amount
        underFlow.capGains = capGains
        underFlow.savings = savingsOut
                
        return underFlow
    
class Withdrawal:
    def __init__(self):
        self.index = []
        self.amount = []
        self.capGains = []
        
        self.savings = []