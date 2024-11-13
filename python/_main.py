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
import os

from numpy.typing import NDArray
from pandas import DataFrame

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
        
        # self.executeSingle()
        self.executeMulti()

        # with open("Outputs/NetWorth1.csv",'w') as f:
        #     for age in range(62,71):
        #         self.vars.benefits.socialSecurity.collectionAge = [age,age]

        #         # self.executeSingle()
        #         self.executeMulti()

        #         print(age)
        #         val = np.sum(self.avgTotalSavings.iloc[-1,:])
        #         print('Final net worth: ',f'{val:,.0f}')
        #         f.write(str(age) + ',' + str(val) + ',' + str(np.percentile(self.totalSavings,25)) + ',' + str(np.percentile(self.totalSavings,75)) + '\n')

        self.toc = time()
        print('Done: ',str(self.toc-self.tic))

    def getTotal(self,summary):
        vals,avgVal = [],[]
        for i,val in enumerate(summary):
            vals.append(np.sum(val.iloc[-1,:]))

            if i == 0:
                avgVal = np.copy(val)
            else:
                avgVal += val

        avgVal /= len(vals)

        return avgVal,vals
    
    def getField(self,fields:list[str],filename:str=None,inflation:NDArray=None):
        vals = []
        avgVal = []

        # Get Data
        for i,vars in enumerate(self.allVars):
            obj = vars
            for field in fields:
                obj = getattr(obj,field)

            vals.append(obj)
            if i == 0:
                avgVal = np.copy(obj)
            else:
                avgVal += obj

        avgVal /= len(vals)
        
        # Add Inflation
        if inflation is None:
            inflation = np.ones(self.vars.base.years)

        if len(np.shape(inflation)) != len(np.shape(avgVal)):
            inflation = np.array([inflation])

        if np.shape(inflation).index(self.vars.base.years) != np.shape(avgVal).index(self.vars.base.years):
            inflation = inflation.transpose()

        avgVal /= inflation

        # Write Output
        if not filename is None:
            # Manage filename
            path = os.path.join(*os.path.normpath('Outputs/' + filename).split(os.sep)[:-1])

            if not os.path.isdir(path):
                os.mkdir(path)

            # Manage Data Type
            match type(avgVal):
                case pd.DataFrame:
                    avgVal.to_csv('Outputs/' + filename)
                case NDArray:
                    pd.DataFrame(avgVal.transpose(),index=np.arange(self.vars.base.years)).to_csv('Outputs/' + filename)

        return avgVal,vals
    
    def executeSingle(self):
        outputs = self.loop()
        
        self.avgTotalSavings,self.totalSavings = self.getTotal(outputs['totalSavings'])
        self.avgTotalSavings *= mp.cpu_count()

        self.avgTotalExpenses,_ = self.getTotal(outputs['totalExpenses'])
        self.avgTotalExpenses *= mp.cpu_count()

        # self.avgTotalExpenses.to_csv('Outputs/Expenses.csv') 
        # self.avgTotalSavings.to_csv('Outputs/Savings.csv')    

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

        # Get Fields
        self.avgInflation,self.summedInflation = self.getField(['salary','summedInflation'],'Inflation.csv')
        self.avgSalary,_ = self.getField(['salary','salary'],'Income/Salary.csv')
        self.avgSS,_ = self.getField(['benefits','socialSecurity','ssIns'],'Income/SocialSecurity.csv')

        self.avgRetire,_ = self.getField(['savings','reports','retireIncome'],'Accounts/401ks.csv')
        self.avgCapGains,_ = self.getField(['savings','reports','capitalGains'],'Accounts/CapitalGains.csv')

        self.avgTaxes,_ = self.getField(['savings','reports','totalTaxes'],'Expense/Taxes.csv')
        self.avgDeductions,_ = self.getField(['savings','reports','totalDeducted'],'Expense/Deductions.csv')
        self.avgWithholdings,_ = self.getField(['savings','reports','totalWithheld'],'Expense/Withholdings.csv')

        self.avgWithdrawals,_ = self.getField(['savings','withdrawals'],'Accounts/Withdrawals.csv')
        self.avgContributions,_ = self.getField(['savings','contributions'],'Accounts/Contributions.csv')
        self.avgEarnings,_ = self.getField(['savings','earnings'],'Accounts/Earnings.csv')

        # Get Summary
        self.savings = pd.concat(self.allSavings)
        self.savings = self.savings.groupby(self.savings.index)

        self.avgTotalSavings,self.totalSavings = self.getTotal(self.allSavings)
        self.avgTotalExpenses,_ = self.getTotal(self.allExpenses)

        self.avgTotalSavings.to_csv('Outputs/Savings.csv')      
        self.avgTotalExpenses.to_csv('Outputs/Expense/Expenses.csv')      

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
            totalSavings.append(self.vars.savings.savings)
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

    with open('Inputs/main.pkl', 'wb') as file:
        pickle.dump(main, file)
    
    # with open('Inputs/main.pkl', 'rb') as file:
    #     main = pickle.load(file)

    print('Max net worth:   ',f'{np.max(np.sum(main.avgTotalSavings,axis=1)):,.0f}')#/main.avgInflation
    print('Final net worth: ',f'{np.sum(main.avgTotalSavings.iloc[-1,:]):,.0f}')#/main.avgInflation[-1]

    plt.figure()
    plt.plot(main.savings.median())
    plt.legend(main.avgTotalSavings.columns)
    plt.plot(np.zeros((main.vars.base.years,1)),'--')
    plt.savefig('Outputs/Accounts')

    plt.figure()
    plt.title('Net Worth')
    std = np.std(main.totalSavings)
    avg = np.mean(main.totalSavings)
    plt.hist(main.totalSavings,#/main.avgInflation[-1],
             bins=max(1,int(main.vars.base.loops/5)),
             rwidth=0.9,
             range=(avg-2*std,avg+3*std))#/main.avgInflation[-1])
    plt.savefig('Outputs/NetWorth')
    
    # accounts = main.vars.accounts
    # accountType = accounts.accountSummary.accountType
    # for accName,accType in accountType.items():
    #     plt.figure()
    #     plt.title(accName)
    #     data = []
    #     for savings in main.allSavings:
    #         data.append(savings[accName].iloc[-1])

    #     std = np.std(data)
    #     avg = np.mean(data)

    #     plt.hist(data,
    #              bins=max(1,int(main.vars.base.loops/20)),
    #              rwidth=0.9,
    #              range=(avg-2*std,avg+3*std))

    plt.show()
    # print('')