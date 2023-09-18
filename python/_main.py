from Vars import Vars
from TaxDict import TaxDict
from Setup import Setup

from Loans import Loans
from Expenses import Expenses

from Taxes import Taxes
from Savings import Savings

import numpy as np

class Main:
    def __init__(self):
        """
        from typing import List
        def pick(l: List[int], index: int) -> int:
            pass
        """

        vars = Vars()
        # totalExpenses = np.zeros((vars.expenses.numExpenses,vars.base.years))
        # totalSavings = np.zeros((vars.allocations.numAccounts,vars.base.years))
        
        for i in range(vars.base.loops):
            vars = Vars()
            taxDict = TaxDict()
            """
            Update arrays to object based maps with names
            """

            # Reader reader = new Reader(vars);
            # reader.run();
            """
            Change all random's to numpy random
            """

            setup = Setup(vars, taxDict)
            vars = setup.run()
            """
            Get 401k totals for minimum distribution
            """

            loans = Loans(vars)
            vars = loans.run()

            expenses = Expenses(vars)
            vars = expenses.run()
            """
            HSA values from healthcare expenses
            Add additional expenses (use Mint)
            """

            taxes = Taxes(vars, taxDict)
            vars = taxes.run()
            """
            Add 401k and SS to income in retirement
            Add Medicare expenses to health
            Add inflation assumption to deductions
            """

            savings = Savings(vars)
            vars = savings.run()
            
        #     totalExpenses = Utility.ArrayMath.sumArrays2D(totalExpenses,vars.expenses.totalExpenses)
        #     totalSavings = Utility.ArrayMath.sumArrays2D(totalSavings,vars.savings.savings)
        
        # vars.expenses.totalExpenses = Utility.ArrayMath.avgArrays2D(totalExpenses,vars.base.loops)
        # vars.savings.savings        = Utility.ArrayMath.avgArrays2D(totalSavings,vars.base.loops)

        self.vars = vars
        
        # print("Net Worth: " + Utility.ArrayMath.sumArray2(vars.savings.savings,1)[vars.base.years-1])
        
#         Writer writer = new Writer(vars);
#         writer.run();
        
        # print("Elapsed time was " + (double)((stopTime - startTime) / 1e9) + " seconds.")

main = Main()

print()