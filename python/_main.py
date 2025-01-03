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
from typing import Any,Optional

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

        # with open("Outputs/NetWorth1.csv",'w') as f:
        #     for age in range(62,71):
        #         self.vars.benefits.socialSecurity.collectionAge = [age,age]

        #         # self.executeSingle()
        #         self.executeMulti()

        #         print(age)
        #         val = np.sum(self.avgTotalSavings.iloc[-1,:])
        #         print('Final net worth: ',f'{val:,.0f}')
        #         f.write(str(age) + ',' + str(val) + ',' + str(np.percentile(self.loopSavings,25)) + ',' + str(np.percentile(self.loopSavings,75)) + '\n')

        self.toc = time()
        print('Done: ',str(self.toc-self.tic))

    def getTotal(self,summary:list[DataFrame]) -> tuple[DataFrame,list[float]]:
        vals = []
        avgVal = pd.DataFrame(0,index=summary[0].index,columns=summary[0].columns)
        for val in summary:
            vals.append(np.sum(val.iloc[-1,:]))
            avgVal += val

        avgVal /= len(summary)

        return avgVal,vals
    
    def getField(self,fields:list[str],filename:str,columns:Optional[list[str]]=None) -> tuple[NDArray,list[Any]]:
        # Get Data
        vals = []
        for i,vars in enumerate(self.allVars):
            obj = vars
            for field in fields:
                obj = getattr(obj,field)

            vals.append(obj)

        avgVal:NDArray = np.mean(vals,axis=0)
        if avgVal.shape[0] != self.vars.base.years:
            avgVal = avgVal.T

        # Write Output
        path = os.path.join(*os.path.normpath('Outputs/' + filename).split(os.sep)[:-1])
        if not os.path.isdir(path):
            os.mkdir(path)

        # Manage Data Type
        pd.DataFrame(avgVal,index=np.arange(self.vars.base.years),columns=columns).to_csv('Outputs/' + filename)

        return avgVal,vals
    
    def executeSingle(self):
        outputs = self.loop()
        
        self.avgTotalSavings,self.totalSavings = self.getTotal(outputs['loopSavings'])
        self.avgTotalExpenses,_ = self.getTotal(outputs['loopExpenses'])

        self.savings = self.avgTotalSavings

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
                self.allVars.extend(result['loopVars'])
                self.allSavings.extend(result['loopSavings'])
                self.allExpenses.extend(result['loopExpenses'])

        # Get Fields
        varsObj:Vars = self.allVars[0]
        columns = varsObj.savings.contributions.columns

        self.avgInflation,self.summedInflation = self.getField(['salary','summedInflation'],'Inflation.csv')
        self.avgSalary,_ = self.getField(['salary','salary'],'Income/Salary.csv')
        self.avgSS,_ = self.getField(['benefits','socialSecurity','ssIns'],'Income/SocialSecurity.csv')

        self.avgRetire,_ = self.getField(['savings','reports','retireIncome'],'Accounts/401ks.csv')
        self.avgCapGains,_ = self.getField(['savings','reports','capitalGains'],'Accounts/CapitalGains.csv')

        self.avgTaxes,_ = self.getField(['savings','reports','totalTaxes'],'Expense/Taxes.csv')
        self.avgDeductions,_ = self.getField(['savings','reports','totalDeducted'],'Expense/Deductions.csv')
        self.avgWithholdings,_ = self.getField(['savings','reports','totalWithheld'],'Expense/Withholdings.csv')

        self.avgWithdrawals,_ = self.getField(['savings','withdrawals'],'Accounts/Withdrawals.csv',columns)
        self.avgContributions,_ = self.getField(['savings','contributions'],'Accounts/Contributions.csv',columns)
        self.avgEarnings,_ = self.getField(['savings','earnings'],'Accounts/Earnings.csv',columns)

        # Get Summary
        self.savings = pd.concat(self.allSavings)
        self.savings = self.savings.groupby(self.savings.index).median()

        self.avgTotalSavings,self.totalSavings = self.getTotal(self.allSavings)
        self.avgTotalExpenses,_ = self.getTotal(self.allExpenses)

        self.avgTotalSavings.to_csv('Outputs/Savings.csv')      
        self.avgTotalExpenses.to_csv('Outputs/Expense/Expenses.csv')      

    def loop(self):
        self.toc = time()
        outputs = {}

        loopVars = []
        loopExpenses = []
        loopSavings = []

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

            loopVars.append(self.vars)
            loopSavings.append(self.vars.savings.savings)
            loopExpenses.append(self.vars.expenses.totalExpenses)

            print('Loop ',str(i+1),'/',str(loops),' done: ',str(time()-self.toc))
            self.toc = time()

        outputs['loopVars'] = loopVars
        outputs['loopSavings'] = loopSavings
        outputs['loopExpenses'] = loopExpenses

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
    plt.plot(main.savings)
    plt.legend(main.avgTotalSavings.columns)
    plt.plot(np.zeros((main.vars.base.years,1)),'--')
    # plt.yscale('log')
    plt.savefig('Outputs/Accounts')

    # plt.figure()
    # plt.title('Net Worth')
    # std = np.std(main.totalSavings)
    # avg = np.mean(main.totalSavings)
    # plt.hist(main.totalSavings,#/main.avgInflation[-1],
    #          bins=max(1,int(main.vars.base.loops/5)),
    #          rwidth=0.9,
    #          range=(avg-2*std,avg+3*std))#/main.avgInflation[-1])
    # plt.savefig('Outputs/NetWorth')
    
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