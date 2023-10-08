from Utility import Utility

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Savings:

    def __init__(self,vars):
        self.vars = vars
        
        self.years = vars.base.years
        self.numInd = vars.base.numInd
        self.ages = vars.base.ages

        self.isKids = vars.children.isKids
        self.childBaseAges = vars.children.childBaseAges
        
        self.netCash = vars.taxes.netCash
        self.numAccounts = len(vars.accounts.__dict__.items())
    
    def run(self):        
        self.allocCalc()
        self.vars.savings.allocations = self.allocations

        self.earningCalc()
        self.vars.savings.earnings = self.earnings
        
        self.savingsCalc()
        self.vars.savings.allocations = self.allocations
        self.vars.savings.earnings = self.earnings
        self.vars.savings.savings = self.savings
        
        return self.vars
    
    
    def allocCalc(self):
        accounts = self.vars.accounts

        tempAllocations = accounts.allocations.copy()

        maxAllocation = tempAllocations.max(axis=None)
        binWidth = int(self.years / (tempAllocations.shape[1] - 1))
        
        self.allocations = pd.DataFrame(index=np.arange(self.years))
        for _, acc in tempAllocations.iterrows():
            self.allocations[acc.name] = np.interp(np.arange(self.years),np.arange(0,self.years+1,binWidth),acc.values) / maxAllocation

        for ind, acc in self.allocations.iterrows():
            self.allocations.iloc[ind] = acc / np.sum(acc)

        self.allocations.to_csv('Allocations.csv')

    def earningCalc(self):
        accounts = self.vars.accounts

        tempEarnings = accounts.earnings.copy()
        
        self.earnings = pd.DataFrame(index=np.arange(self.years))
        values = []
        for _, acc in tempEarnings.iterrows():
            if any(np.isnan(acc.values)):
                values = np.random.normal(acc.values[0],acc.values[1],self.years)
            else:
                mu    = np.interp(np.arange(self.years),[0,self.years],[acc.values[0],acc.values[2]])
                sigma = np.interp(np.arange(self.years),[0,self.years],[acc.values[1],acc.values[3]])
                
                values = [np.random.normal(mu[j],sigma[j]) for j in range(self.years)]
            
            match accounts.accountSummary.accountType[acc.name].upper():
                case 'SAVINGS': values = [0 if v < 0 else v for v in values]
            
            values = [-0.99 if v <= -1 else v for v in values]

            self.earnings[acc.name] = values 

        self.earnings.to_csv('Earnings.csv')
    
    def savingsCalc(self):
        savings = self.vars.savings
        expenses = self.vars.expenses
        accounts = self.vars.accounts

        ret = self.vars.benefits.retirement
        
        # EXPENSES
        self.expenses = pd.DataFrame(0,index=np.arange(self.years),columns=savings.earnings.columns)
        for _,acc in expenses.__dict__.items():
            if hasattr(acc,'allocation'):
                self.expenses[acc.allocation] += acc.total
        
        self.expenses.to_csv('Expenses.csv')

        # SAVINGS
        self.savings = pd.DataFrame(0,index=np.arange(self.years),columns=savings.earnings.columns)
        for accName,_ in savings.earnings.items():
            for j in range(self.years):
                # Base savings
                if j == 0:
                    self.savings[accName][0] += accounts.accountSummary.baseSavings[accName]
                else:
                    self.savings[accName][j] += self.savings[accName][j-1]

                # Allocation of net cash and retirement contributions
                self.savings[accName][j] += self.allocations[accName][j] * self.netCash[j]

                match accounts.accountSummary.accountType[accName].upper():
                    case 'ROTH': self.savings[accName][j] += ret.netRothCont[j]
                    case 'TRAD': self.savings[accName][j] += ret.netTradCont[j]
            
                # Remove expenses and retirement distributions
                self.savings[accName][j] -= self.expenses[accName][j]

                match accounts.accountSummary.accountType[accName].upper():
                    case 'ROTH','TRAD':
                        rmdDist = 0
                        for ind in range(self.numInd):
                            ageFactor = self.ages[ind] * np.power(ret.rmdFactor[0],2) + self.ages[ind] * ret.rmdFactor[1] + ret.rmdFactor[2]
                            rmdDist += self.savings[accName][j] / ageFactor
                    
                        self.savings[accName][j] -= rmdDist

                # Remove college
                match accName.upper():
                    case 'COLLEGE529':
                        if j > -max(self.childBaseAges) and self.isKids[j] == 0:
                            remainVal = self.savings[accName][j]
                            self.savings[accName][j] = 0
                            self.savings['longTermSavings'][j] += remainVal
                        
                # Add earnings
                self.savings[accName][j] *= 1 + self.earnings[accName][j]

        self.savings.to_csv('Savings.csv')        

        n=4
        plt.plot(self.savings.iloc[:,-n:])    
        plt.legend(self.savings.columns[-n:])
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
    
    def overFlow(self, yr, maxVal, accFrom, accTo):
        accounts = self.vars.accounts

        overFlow = Withdrawal()
        
        index = accFrom
        amount = 0
        capGains = accounts.accountSummary.capGainsType[accFrom]
        savingsOut = savingsIn
        
        if self.savings[accFrom][yr] > maxVal:
            amount = savingsOut[accFrom][yr] - maxVal
            savingsOut[accFrom][yr] = maxVal
            savingsOut[accTo][yr] += amount

        overFlow.index = index
        overFlow.amount = amount
        overFlow.capGains = capGains
        overFlow.savings = savingsOut
        
        return overFlow
    
    
    def underFlow(self, savingsIn, yr, indTo, indFrom):
        accounts = self.vars.accounts

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