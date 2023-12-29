import numpy as np
import matplotlib.pyplot as plt

class Loans:
    def __init__(self, vars):
        self.vars = vars
        self.years = vars.base.years
    
    def run(self):
        """GENERAL LOANS"""
        self.loanBal  = np.zeros(self.years)
        self.loanPay  = np.zeros(self.years)
        self.loanPrn  = np.zeros(self.years)
        self.loanInt  = np.zeros(self.years)
        self.loanWth  = np.zeros(self.years)
        self.loanDwn  = np.zeros(self.years)

        loan = self.vars.loans
        for i in range(loan.numLoans):
            [loan.loanBal, 
             loan.loanPay, 
             loan.loanPrn, 
             loan.loanInt, 
             _, 
             _]  = self.loanCalc(loan.loanSummary.loanYr[i],
                                 loan.loanSummary.term[i],
                                 loan.loanSummary.rate[i],
                                 loan.loanSummary.prin[i])
            
        """HOUSING LOANS"""
        self.loanBal  = np.zeros(self.years)
        self.loanPay  = np.zeros(self.years)
        self.loanPrn  = np.zeros(self.years)
        self.loanInt  = np.zeros(self.years)
        self.loanWth  = np.zeros(self.years)
        self.loanDwn  = np.zeros(self.years)

        house = self.vars.expenses.house
        for i in range(house.numHouses):
            sellPrev = False if i == 0 else True

            [house.houseBal, 
             house.housePay, 
             house.housePrn, 
             house.houseInt, 
             house.houseWth, 
             house.houseDwn]  = self.loanCalc(house.houseSummary.purYr[i],
                                              house.houseSummary.term[i],
                                              house.houseSummary.rate[i],
                                              house.houseSummary.prin[i],
                                              house.houseSummary.sellYr[i],
                                              house.houseSummary.down[i],
                                              house.houseSummary.app[i],
                                              sellPrev)
        # plt.plot(house.houseWth)
        # plt.show()

        """CAR LOANS"""
        self.loanBal  = np.zeros(self.years)
        self.loanPay  = np.zeros(self.years)
        self.loanPrn  = np.zeros(self.years)
        self.loanInt  = np.zeros(self.years)
        self.loanWth  = np.zeros(self.years)
        self.loanDwn  = np.zeros(self.years)
        
        cars = self.vars.expenses.cars
        for i in range(cars.numCars):        
            [cars.carBal, 
             cars.carPay, 
             cars.carPrn, 
             cars.carInt, 
             cars.carWth, 
             cars.carDwn]  = self.loanCalc(cars.carSummary.purYr[i],
                                           cars.carSummary.term[i],
                                           cars.carSummary.rate[i],
                                           cars.carSummary.prin[i],
                                           cars.carSummary.sellYr[i],
                                           cars.carSummary.down[i],
                                           cars.carSummary.app[i])
        
        return self.vars
    
    def loanCalc(self,
                 purYr, term, rate, prin, 
                 sellYr=None, down=None, app=None, 
                 sellPrev=False):
        """
        INPUTS
            purYr - purchase year
            term - (years) length of loan 
            rate - (%) annual interest rate
            prin - principal loan amount

            sellYr - [OPT] sell year
            down - [OPT] (%) down payment based on initial principal
            app - [OPT] (%) annual appreciation

            sellPrev - [OPT] (bool) selling previous loan
        """
        
        """INITIALIZE LOAN VALUES"""
        rate /= 12
        term *= 12
        app = app / 12 if not app is None else 0

        purYr = int(purYr)
        sellYr = int(sellYr) if not sellYr is None else -1
        
        downPay = down * prin if not down is None else 0

        prinPay = prin - self.loanWth[purYr-1] + self.loanBal[purYr-1] if sellPrev else prin
        prinPay = 0 if prinPay < downPay else prinPay - downPay
        
        monthBal,monthPay,monthPrn,monthInt,monthWth = np.zeros(12),np.zeros(12),np.zeros(12),np.zeros(12),np.zeros(12)

        """CREATE LOAN ARRAY SIZES BASED ON PURCHASE YEAR"""
        arrSize = int(self.years + abs(purYr) if purYr < 0 else self.years)
        yrInd = int(0 if purYr < 0 else purYr)
        end = int((sellYr - purYr) * 12 if sellYr > purYr else self.years * 12)
        
        yearBal,yearPay,yearPrn,yearInt,yearWth = np.zeros(arrSize),np.zeros(arrSize),np.zeros(arrSize),np.zeros(arrSize),np.zeros(arrSize)
        
        mthInd = 0
        for i in range(end):
            termConst = np.power((1 + rate),term)
            
            """GET MONTHLY COMPOUNDED VALUES"""
            if i < term:
                monthBal[mthInd] = prinPay * (termConst - np.power((1 + rate),i+1)) / (termConst - 1)
                monthPay[mthInd] = prinPay * (rate * termConst) / (termConst - 1)
                if monthBal[mthInd] < 0:
                    monthPay[mthInd] += monthBal[mthInd]
                    monthBal[mthInd] = 0

                if i % 12 > 0:
                    monthPrn[mthInd] = monthBal[mthInd-1] - monthBal[mthInd]
                elif yrInd == purYr or yrInd == 0:
                    monthPrn[mthInd] = prinPay - monthBal[mthInd]
                else:
                    monthPrn[mthInd] = yearBal[yrInd-1] - monthBal[mthInd]
                
                monthInt[mthInd] = monthPay[mthInd] - monthPrn[mthInd]
            else:
                monthBal[mthInd] = 0
                monthPay[mthInd] = 0
                monthPrn[mthInd] = 0
                monthInt[mthInd] = 0
            
            monthWth[mthInd] = prin * np.power((1 + app),i)
            
            """SUM UP YEARLY VALUES"""
            if mthInd == 11:
                if i < term:
                    yearBal[yrInd] = monthBal[mthInd]
                    yearPay[yrInd] = np.sum(monthPay)
                    yearPrn[yrInd] = np.sum(monthPrn)
                    yearInt[yrInd] = np.sum(monthInt)
                else:
                    yearBal[yrInd] = 0
                    yearPay[yrInd] = 0
                    yearPrn[yrInd] = 0
                    yearInt[yrInd] = 0
                
                yearWth[yrInd]  = monthWth[mthInd]
                
                yrInd += 1
                mthInd = 0

                if yrInd >= arrSize:
                    break
                
            else:
                mthInd += 1
        
        """RESET ARRAY SIZES IF PURCHASE IS PRIOR TO CURRENT YEAR"""
        if (purYr < 0):
            yearBal = yearBal[int(abs(purYr)):int(abs(purYr)+self.years)]
            yearPay = yearPay[int(abs(purYr)):int(abs(purYr)+self.years)]
            yearPrn = yearPrn[int(abs(purYr)):int(abs(purYr)+self.years)]
            yearInt = yearInt[int(abs(purYr)):int(abs(purYr)+self.years)]
            yearWth = yearWth[int(abs(purYr)):int(abs(purYr)+self.years)]
        
        """SUM INTO TOTAL LOAN VALUES"""
        self.loanBal  = np.sum((self.loanBal,yearBal),0)
        self.loanPay  = np.sum((self.loanPay,yearPay),0)
        self.loanPrn  = np.sum((self.loanPrn,yearPrn),0)
        self.loanInt  = np.sum((self.loanInt,yearInt),0)        
        self.loanWth  = np.sum((self.loanWth,yearWth),0)

        if purYr >= 0:
            self.loanDwn[purYr] += downPay

        return self.loanBal, self.loanPay, self.loanPrn, self.loanInt, self.loanWth, self.loanDwn