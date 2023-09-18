import numpy as np
import math

class Savings:

    def __init__(self,vars):
        self.vars = vars
        
        self.years = vars.base.years
        self.numInd = vars.base.numInd
        
        self.netCash = vars.taxes.netCash
        self.numAccounts = vars.allocations.numAccounts
        # self.accountName = vars.allocations.accountName
    
    def run(self):
        self.savings = np.zeros((self.numAccounts,self.years))
        self.contributions = np.zeros((self.numAccounts,self.years))
        self.withdrawals = np.zeros((self.numAccounts,self.years))
        
        self.allocations = self.allocCalc(self.vars.allocations.allocations)
        self.earnings = self.earningCalc(self.vars.allocations.earnings,self.vars.allocations.accountType)
        
        self.savingsCalc()
        self.vars.savings.allocations = self.allocations
        self.vars.savings.earnings = self.earnings
        self.vars.savings.contributions = self.contributions
        self.vars.savings.savings = self.savings
        self.vars.savings.withdrawals = self.withdrawals
        
        return self.vars
    
    
    def allocCalc(self,allocs):
        allocations = np.zeros((len(allocs),self.years))
        
        binWid = int(self.years / (len(allocs[0]) - 1))
        maxAllocation = 
        
        for i in range(self.numAccounts):
            for j in range(self.years):
                if (j == 0):
                    allocations[i,j] = allocs[i][0] / 10
                else:
                    curBin = int(math.floor(j / binWid))
                    allocations[i,j] = (allocs[i][curBin] + (((j % binWid) / binWid) * (allocs[i][curBin+1] - allocs[i][curBin]))) / 100
        
        totalAllocations = np.sum(allocations,0)
        for i in range(self.numAccounts):
            for j in range(self.years):
                allocations[i,j] /= totalAllocations[j]

        return allocations
    
    
    def earningCalc(self,earns,accType):
        earnings = np.zeros((len(earns),self.years))
        
        for i in range(self.numAccounts):
            for j in range(self.years):
                if len(earns[i]) == 2:
                    earnings[i,j] = np.random.normal(earns[i][0],earns[i][1])
                else:
                    mus    = [earns[i][0],earns[i][2]]
                    sigmas = [earns[i][1],earns[i][3]]

                    mu    = mus[0] - ((j / self.years) * (mus[0] - mus[1]))
                    sigma = sigmas[0] - ((j / self.years) * (sigmas[0] - sigmas[1]))

                    earnings[i,j] = np.random.normal(mu,sigma)
                
                if accType[i].upper() == "SAVINGS":
                    if (earnings[i,j] < 0):
                        earnings[i,j] = 0
                    
                earnings[i,j] /= 100
            
        return earnings
    
    
    def savingsCalc(self):
        ret = self.vars.benefits.retirement
        exps = self.vars.expenses
        house = self.vars.expenses.housing.house
        cars = self.vars.expenses.cars
        
        expenses = self.numAccounts
                       
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
            for i in range(self.numAccounts):
                match (self.accountName[i].upper()):
                    case "COLLEGE 529":
                        expenses[i] = exps.education.totalEd[j]
                    
                    case "LONG-TERM SAVINGS":
                        expenses[i] = house.houseDwn[j] + cars.carDwn[j] + exps.major.totalMajor[j]  
                    
                    case "SHORT-TERM SAVINGS":
                        expenses[i] = exps.vacation.totalVac[j] + exps.charity.totalChar[j] + exps.random.totalRand[j]  
                    
                    case "SPENDING":
                        expenses[i] = exps.housing.rent.totalRent[j] + exps.housing.house.totalHouse[j] + exps.cars.totalCar[j] + \
                                      exps.food.totalFood[j] + exps.entertain.totalEnt[j] + exps.personalCare.totalPers[j] + \
                                      exps.healthcare.totalHealth[j] + exps.pet.totalPet[j] + exps.holiday.totalHol[j]  
            
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
                    self.savings[i,j] += self.vars.allocations.baseSavings[i]
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
            for under in self.vars.allocations.underflow:
                if (len(under) == 3):
                    if (j >= under[2][0]):
                        self.withdrawal = self.underFlow(self.savings,j,under[0][0],under[1])
                        self.savings = self.withdrawal.savings
                    
                else:
                    self.withdrawal = self.underFlow(self.savings,j,under[0][0],under[1])
                    self.savings = self.withdrawal.savings
                
            # OVERFLOW
            for over in self.vars.allocations.overflow:
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
        capGains = self.vars.allocations.capGainsType[indFrom]
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
                capGains[i] = self.vars.allocations.capGainsType[i]
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