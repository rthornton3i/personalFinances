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

        setup = Setup(self.vars, self.taxDict)
        self.vars = setup.run()

        loans = Loans(self.vars)
        self.vars = loans.run()

        self.toc = time()
        print('Initial setup done: ',str(self.toc-self.tic))

        self.executeSingle()
        # self.executeMulti()

        self.toc = time()
        print('Done: ',str(self.toc-self.tic))

    def executeSingle(self):
        outputs = self.loop()
        self.totalSavings = []
        for t in ['totalSavings','totalExpenses']:
            total = pd.DataFrame()
            for i,output in enumerate(outputs[t]):
                self.totalSavings.append(np.sum(output.iloc[-1,:]))
                if i == 0:
                    total = output
                else:
                    total += output

            if t == 'totalSavings':
                self.avgTotalSavings = total / (self.vars.base.loops / mp.cpu_count())
            else:
                self.avgTotalExpenses = total / (self.vars.base.loops / mp.cpu_count()) 

    def executeMulti(self):
        def getTotal(summary):
            total = 0
            endVal = []
            for i,val in enumerate(summary):
                endVal.append(np.sum(val.iloc[-1,:]))

                if i == 0:
                    total = val
                else:
                    total += val

            return total,endVal
        
        totalSavings = []
        totalExpenses = []
        with Pool(processes=mp.cpu_count()) as pool:
            results = [pool.apply_async(self.loop) for _ in range(mp.cpu_count())]

            pool.close()
            pool.join()

            [r.wait() for r in results]
            for r in results:
                result = r.get()
                totalSavings.extend(result['totalSavings'])
                totalExpenses.extend(result['totalExpenses'])

        total,self.totalSavings = getTotal(totalSavings)
        self.avgTotalSavings = total / self.vars.base.loops
        total,_ = getTotal(totalExpenses)
        self.avgTotalExpenses = total / self.vars.base.loops

        self.avgTotalSavings.to_csv('Outputs/Savings.csv')      
        self.avgTotalExpenses.to_csv('Outputs/Expenses.csv')      

    def loop(self):
        self.toc = time()
        outputs = {}

        totalExpenses = []
        totalSavings = []

        loops = int(np.ceil(self.vars.base.loops / mp.cpu_count()))
        for i in range(loops):
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

            totalSavings.append(self.vars.savings.savings)
            totalExpenses.append(self.vars.expenses.totalExpenses)

            print('Loop ',str(i+1),'/',str(loops),' done: ',str(time()-self.toc))
            self.toc = time()

        outputs['totalSavings'] = totalSavings
        outputs['totalExpenses'] = totalExpenses

        return outputs

if __name__ == '__main__':
    import pickle

    main = Main()

    with open('Inputs/main.pkl', 'wb') as file:
        pickle.dump(main, file)
    
    # with open('Inputs/main.pkl', 'rb') as file:
    #     main = pickle.load(file)

    print(f'{np.sum(main.avgTotalSavings.iloc[-1,:]):,.0f}')

    plt.figure()
    n = len(main.avgTotalSavings.columns)
    plt.plot(main.avgTotalSavings.iloc[:,-n:])    
    plt.legend(main.avgTotalSavings.columns[-n:])
    plt.plot(np.zeros((main.vars.base.years,1)),'--')
    plt.show()

    plt.figure()
    plt.hist(main.totalSavings,bins=max(1,int(main.vars.base.loops/20)),rwidth=0.9)
    plt.show()
