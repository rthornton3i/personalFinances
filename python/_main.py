from Vars import Vars
from TaxDict import TaxDict
from Setup import Setup

from Loans import Loans
from Expenses import Expenses

from Taxes import Taxes
from Savings import Savings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import multiprocessing as mp
from multiprocessing import Pool
from time import time

"""
from typing import List
def pick(l: List[int], index: int) -> int:
    pass
"""

class Main:
    def __init__(self):
        self.tic = time()

        self.vars = Vars()
        self.taxDict = TaxDict()

        loans = Loans(self.vars)
        self.vars = loans.run()
        """
        Add refinancing
        Add loan forgiveness and income driven plan
        """

        self.toc = time()
        print('Initial setup done: ',str(self.toc-self.tic))

        self.executeSingle()
        # self.executeMulti()

        self.toc = time()
        print('Done: ',str(self.toc-self.tic))

    def getTotal(self,summary):
        total = 0
        endVal = []
        for i,val in enumerate(summary):
            endVal.append(np.sum(val.iloc[-1,:]))

            if i == 0:
                total = val
            else:
                total += val

        avg = total / self.vars.base.loops

        return avg,endVal
    
    def executeSingle(self):
        outputs = self.loop()
        
        self.avgTotalSavings,self.totalSavings = self.getTotal(outputs['totalSavings'])
        self.avgTotalSavings *= mp.cpu_count()

        self.avgTotalExpenses,_ = self.getTotal(outputs['totalExpenses'])
        self.avgTotalExpenses *= mp.cpu_count()

        self.avgTotalExpenses.to_csv('Outputs/Expenses.csv') 
        self.avgTotalSavings.to_csv('Outputs/Savings.csv')    

    def executeMulti(self):  
        self.allVars = []      
        self.allSavings = []
        self.allExpenses = []
        with Pool(processes=mp.cpu_count()) as pool:
            results = [pool.apply_async(self.loop) for _ in range(mp.cpu_count())]

            pool.close()
            pool.join()

            [r.wait() for r in results]
            for r in results:
                result = r.get()
                self.allVars.extend(result['totalVars'])
                self.allSavings.extend(result['totalSavings'])
                self.allExpenses.extend(result['totalExpenses'])

        self.avgTotalSavings,self.totalSavings = self.getTotal(self.allSavings)
        self.avgTotalExpenses,_ = self.getTotal(self.allExpenses)

        self.avgTotalSavings.to_csv('Outputs/Savings.csv')      
        self.avgTotalExpenses.to_csv('Outputs/Expenses.csv')      

    def loop(self):
        self.toc = time()
        outputs = {}

        totalVars = []
        totalExpenses = []
        totalSavings = []

        loops = int(np.ceil(self.vars.base.loops / mp.cpu_count()))
        for i in range(loops):
            setup = Setup(self.vars, self.taxDict)
            self.vars = setup.run()

            expenses = Expenses(self.vars)
            self.vars = expenses.run()
            """
            HSA values from healthcare expenses
            Add additional expenses (use Mint)
            """

            savings = Savings(self.vars)
            self.vars = savings.run()

            taxes = Taxes(self.vars, self.taxDict)
            self.vars = taxes.run()
            """
            Add Medicare expenses to health
            Account for std deduction when retired
            """

            totalVars.append(self.vars)
            totalSavings.append(self.vars.taxes.savings)
            totalExpenses.append(self.vars.expenses.totalExpenses)

            print('Loop ',str(i+1),'/',str(loops),' done: ',str(time()-self.toc))
            self.toc = time()

        outputs['totalVars'] = totalVars
        outputs['totalSavings'] = totalSavings
        outputs['totalExpenses'] = totalExpenses

        return outputs

if __name__ == '__main__':
    import pickle

    main = Main()

    # with open('Inputs/main.pkl', 'wb') as file:
    #     pickle.dump(main, file)
    
    # with open('Inputs/main.pkl', 'rb') as file:
    #     main = pickle.load(file)

    print('Max net worth:   ',f'{np.max(np.sum(main.avgTotalSavings,axis=1)/main.vars.salary.summedInflation):,.0f}')
    print('Final net worth: ',f'{np.sum(main.avgTotalSavings.iloc[-1,:])/main.vars.salary.summedInflation[-1]:,.0f}')

    plt.figure()
    n = len(main.avgTotalSavings.columns)
    plt.plot(main.avgTotalSavings.iloc[:,-n:])    
    plt.legend(main.avgTotalSavings.columns[-n:])
    plt.plot(np.zeros((main.vars.base.years,1)),'--')
    # plt.show()

    plt.figure()
    std = np.std(main.totalSavings)
    avg = np.mean(main.totalSavings)
    plt.hist(main.totalSavings/main.vars.salary.summedInflation[-1],
             bins=max(1,int(main.vars.base.loops/20)),
             rwidth=0.9,
             range=(avg-2*std,avg+3*std)/main.vars.salary.summedInflation[-1])
    plt.show()

    # plt.figure()
    # accounts = main.vars.accounts
    # accountType = accounts.accountSummary.accountType
    # for acc,accType in accountType.items():
    #     main.allSavings
    #     plt.hist()

    print('')