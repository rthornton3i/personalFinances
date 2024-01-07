import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

class Savings:

    def __init__(self,vars):
        self.vars = vars
        
        self.years = vars.base.years
    
    def run(self):    
        savings = self.vars.savings    

        self.allocCalc()
        savings.allocations = self.allocations

        self.earningCalc()
        savings.earnings = self.earnings
        
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

        # self.allocations.to_csv('Allocations.csv')

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
            
            match str(accounts.accountSummary.accountType[acc.name]).upper():
                case 'SAVINGS': values = [0 if v < 0 else v for v in values]
            
            values = [-0.99 if v <= -1 else v for v in values]

            self.earnings[acc.name] = values 

        # self.earnings.to_csv('Earnings.csv')