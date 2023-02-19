import numpy as np
import math

class Loans:
    def __init__(self, vars):
        self.vars = vars
        self.years = vars.base.years
        
        self.house = vars.expenses.housing.house
        self.car = vars.expenses.cars
    
    def run(self):
        self.loanBal  = np.zeros(self.years)
        self.loanPay  = np.zeros(self.years)
        self.loanPrn  = np.zeros(self.years)
        self.loanInt  = np.zeros(self.years)
        self.loanWth  = np.zeros(self.years)
        self.loanDwn  = np.zeros(self.years)

        # Housing Loans
        for i in range(self.house.numHouses):
            sellPrev = False if i == 0 else True

            [self.vars.expenses.housing.house.houseBal, \
            self.vars.expenses.housing.house.housePay, \
            self.vars.expenses.housing.house.housePrn, \
            self.vars.expenses.housing.house.houseInt, \
            self.vars.expenses.housing.house.houseWth, \
            self.vars.expenses.housing.house.houseDwn]  = self.loanCalc(self.house.purYr[i], \
                                                                        self.house.sellYr[i], \
                                                                        self.house.term[i], \
                                                                        self.house.rate[i], \
                                                                        self.house.prin[i], \
                                                                        self.house.down[i], \
                                                                        self.house.app[i], \
                                                                        sellPrev)
        
        # Reset Loan Variables
        self.loanBal  = np.zeros(self.years)
        self.loanPay  = np.zeros(self.years)
        self.loanPrn  = np.zeros(self.years)
        self.loanInt  = np.zeros(self.years)
        self.loanWth  = np.zeros(self.years)
        self.loanDwn  = np.zeros(self.years)
        
        # Car Loans
        for i in range(self.car.numCars):        
            [self.vars.expenses.cars.carBal, \
            self.vars.expenses.cars.carPay, \
            self.vars.expenses.cars.carPrn, \
            self.vars.expenses.cars.carInt, \
            self.vars.expenses.cars.carWth, \
            self.vars.expenses.cars.carDwn]  = self.loanCalc(self.car.purYr[i], \
                                                            self.car.sellYr[i], \
                                                            self.car.term[i], \
                                                            self.car.rate[i], \
                                                            self.car.prin[i], \
                                                            self.car.down[i], \
                                                            self.car.app[i])
        
        return self.vars
    
    def loanCalc(self,purYr, sellYr, term, rate, prin, down, app, sellPrev=False):
        # Up to 1 house from previous year and 1 previous balance/worth
        
        rate /= 100 * 12
        app /= 100 * 12
        down /= 100
        term *= 12
        
        downPay = down * prin
        prinPay = prin - self.loanWth[purYr-1] + self.loanBal[purYr-1] if sellPrev else prin
        prinPay = 0 if prinPay < downPay else prinPay - downPay
        
        monthBal,monthPay,monthPrn,monthInt,monthWth = np.zeros(12),np.zeros(12),np.zeros(12),np.zeros(12),np.zeros(12)

        arrSize = self.years + abs(purYr) if purYr < 0 else self.years
        yrInd = 0 if purYr < 0 else purYr        
        end = (sellYr - purYr) * 12 if sellYr > purYr else self.years * 12        
        
        yearBal,yearPay,yearPrn,yearInt,yearWth = np.zeros(arrSize),np.zeros(arrSize),np.zeros(arrSize),np.zeros(arrSize),np.zeros(arrSize)
        
        mthInd = 0
        for i in range(end):
            termConst = math.pow((1 + rate),term)
            
            if i < term:
                monthBal[mthInd] = prinPay * (termConst - math.pow((1 + rate),i+1)) / (termConst - 1)
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
            
            monthWth[mthInd] = prin * math.pow((1 + app),i)
            
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
            
        if (purYr < 0):
            yearBal = yearBal[int(abs(purYr)):int(abs(purYr)+self.years)]
            yearPay = yearPay[int(abs(purYr)):int(abs(purYr)+self.years)]
            yearPrn = yearPrn[int(abs(purYr)):int(abs(purYr)+self.years)]
            yearInt = yearInt[int(abs(purYr)):int(abs(purYr)+self.years)]
            yearWth = yearWth[int(abs(purYr)):int(abs(purYr)+self.years)]
        
        self.loanBal  = np.sum((self.loanBal,yearBal),0)
        self.loanPay  = np.sum((self.loanPay,yearPay),0)
        self.loanPrn  = np.sum((self.loanPrn,yearPrn),0)
        self.loanInt  = np.sum((self.loanInt,yearInt),0)        
        self.loanWth  = np.sum((self.loanWth,yearWth),0)

        if purYr >= 0:
            self.loanDwn[purYr] += downPay

        return self.loanBal, self.loanPay, self.loanPrn, self.loanInt, self.loanWth, self.loanDwn