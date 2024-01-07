import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Expenses:
    def __init__(self, vars):
        self.vars = vars
        
        self.years = vars.base.years
        self.numInd = vars.base.numInd
        self.iters = vars.filing.iters
        
        self.income = vars.salary.income
        self.inflation = vars.salary.inflation
        self.summedInflation = vars.salary.summedInflation
        
        self.isKids = self.vars.children.isKids
        self.childAges = vars.children.childAges
        self.maxChildYr = vars.children.maxChildYr
        self.childInflation = vars.children.childInflation
    
    def run(self):
        exp =  self.vars.expenses
        exps = [e for e in dir(exp) if not e.startswith('__') and not callable(getattr(exp, e)) and hasattr(getattr(exp,e),'allocation')]

        exp.totalExpenses = pd.DataFrame(0,index=np.arange(self.years),columns=exps)

        exp.totalExpenses.house += self.rentExp()
        exp.totalExpenses.house += self.housingExp()
        exp.totalExpenses.cars = self.carExp()
        exp.totalExpenses.loans = self.loanExp()
        
        exp.totalExpenses.food = self.foodExp()
        exp.totalExpenses.entertain = self.entExp()
        exp.totalExpenses.personalCare = self.personalExp()
        exp.totalExpenses.healthcare = self.healthExp()
        exp.totalExpenses.pet = self.petExp()
        
        exp.totalExpenses.holiday = self.holidayExp()
        exp.totalExpenses.education = self.edExp()
        exp.totalExpenses.vacation = self.vacExp()
        
        exp.totalExpenses.charity = self.charExp()
        exp.totalExpenses.major = self.majExp()
        exp.totalExpenses.random = self.randExp()

        exp.total = np.sum(exp.totalExpenses,axis=0)

        # exps = [exp.rent,exp.house,exp.cars,exp.food,exp.entertain,exp.personalCare,exp.healthcare,exp.pet,exp.holiday,exp.education,exp.vacation,exp.charity,exp.major,exp.random]
        # legend = ['rent','house','cars','food','entertain','personalCare','healthcare','pet','holiday','education','vacation','charity','major','random']
        # for e in exps:
        #     plt.plot(e.total)
        # plt.legend(legend)
        
        # plt.plot(exp.totalExpenses)
        # plt.show()

        return self.vars
    
    def rentExp(self):
        rent = self.vars.expenses.rent
        
        total = np.zeros(self.years)
        
        if len(rent.rentYr) > 0:
            rentExp = (rent.baseRent + np.nansum(rent.rentFees)) * 12
            rentExp += (rent.insurance + rent.electricity + rent.gas + rent.water) * 12
            
            for i in range(rent.rentYr[0],rent.rentYr[1]+1):
                rentExp *= 1 + self.inflation[i]

                total[i] = rentExp
                total[i] += np.random.triangular(rent.repairs[0],rent.repairs[1],rent.repairs[2])
        
        return total
    
    def housingExp(self):
        house = self.vars.expenses.house
        
        total = np.zeros(self.years)
        
        if house.numHouses > 0:
            firstYear = int(0 if house.houseSummary.purYr[0] < 0 else house.houseSummary.purYr[0])
            houseRatio = [0 if i < firstYear else house.houseWth[i] / house.houseWth[firstYear] for i in range(self.years)]

            homeUtil = (house.electricity + house.gas + house.water + house.sewage) * 12
            for i in range(firstYear,self.years):
                # homeUtil *= 1 + self.inflation[i]

                total[i] = house.housePay[i]
                total[i] += (np.random.triangular(house.repairs[0],house.repairs[1],house.repairs[2]) + house.insurance) * houseRatio[i]
                total[i] += homeUtil * houseRatio[i]
            
            total += house.houseDwn

        return total
    
    def loanExp(self):
        loans = self.vars.expenses.loans
        
        total = np.zeros(self.years)

        if loans.numLoans > 0:
            for i in range(self.years):
                total[i] = loans.loanPay[i]

        return total
    
    def carExp(self):     
        cars = self.vars.expenses.cars
        
        total = np.zeros(self.years)

        if cars.numCars > 0:
            firstYear = 0 if cars.carSummary.purYr[0] < 0 else cars.carSummary.purYr[0]
            carRatio = [cars.carWth[i] / cars.carWth[0] for i in range(firstYear,self.years)]
            
            carExps = (cars.insurance + cars.ezpass + cars.fuel) * 12
            for i in range(self.years):
                # carExps *= 1 + self.inflation[i]

                total[i] = cars.carPay[i]
                total[i] += (np.random.triangular(cars.repairs[0],cars.repairs[1],cars.repairs[2]) * 12) * carRatio[i]    
                total[i] += carExps * carRatio[i]

            total += cars.carDwn

        return total
    
    def foodExp(self):        
        food = self.vars.expenses.food
        
        total = np.zeros(self.years)

        foodExps = (food.groceries + food.restaurants + food.otherFood) * 12
        for i in range(self.years):
            foodExps *= 1 + self.inflation[i]
            total[i] = foodExps * (1 + self.childInflation[i])
            
        return total
    
    def entExp(self):
        entertain = self.vars.expenses.entertain
        
        total = np.zeros(self.years)
        
        entertainExps = (entertain.internet + entertain.phone + np.nansum(entertain.tv) + np.nansum(entertain.software) + np.nansum(entertain.memberships)) * 12
        for i in range(self.years):
            entertainExps *= 1 + self.inflation[i]
            total[i] = entertainExps * (1 + self.childInflation[i])

        return total
    
    def personalExp(self):
        personalCare = self.vars.expenses.personalCare
        
        total = np.zeros(self.years)
        
        persExps = (personalCare.clothing + personalCare.shoes + personalCare.hair + personalCare.makeup + personalCare.products) * 12
        for i in range(self.years):
            persExps *= 1 + self.inflation[i]
            total[i] = persExps * (1 + self.childInflation[i])
        
        return total
    
    def healthExp(self):
        health = self.vars.expenses.healthcare

        numVisits = np.zeros((self.iters,self.years))

        total =np.zeros((self.iters,self.years))

        for j in range(self.years):
            for i in range(self.iters):
                numVisits = np.round(np.random.triangular(health.visits[0],health.visits[1],health.visits[2])).astype(int)

                deductible = health.deductible[i]
                maxOOP = health.maxOOP[i]
                for _ in range(numVisits):
                    cost = np.random.triangular(health.costs[0],health.costs[1],health.costs[2])
                    
                    while cost > 0:
                        if deductible > 0:
                            if cost > deductible:
                                total[i,j] += deductible
                                maxOOP -= deductible
                                
                                cost -= deductible
                                deductible = 0
                            else:
                                total[i,j] += cost
                                maxOOP -= cost
                                
                                deductible -= cost
                                cost = 0
                        elif maxOOP > 0:
                            cost *= health.coinsurance[i]
                            if cost > maxOOP:
                                total[i,j] += maxOOP
                                maxOOP = 0
                            else:
                                total[i,j] += cost
                                maxOOP -= cost

                            cost = 0
                        else:
                            cost = 0
                
                total[i,j] += health.drugs * 12
                total[i,j] *= (1 + self.childInflation[i]) / self.iters
        
        return np.sum(total, 0)
    
    def petExp(self):
        pet = self.vars.expenses.pet
        
        total = np.zeros(self.years)
        
        petExps = (pet.food + pet.essentials + pet.toys + pet.careTaker + pet.vet) * 12
        for i in range(self.years):
            petExps *= 1 + self.inflation[i]
            total[i] = petExps
        
        return total
    
    def holidayExp(self):        
        holiday = self.vars.expenses.holiday

        familyGift = np.zeros(self.years)
        childGift = np.zeros(self.years)
        total = np.zeros(self.years)
        
        giftExps = holiday.familyBday + holiday.familyXmas 
        for i in range(self.years):
            giftExps *= 1 + self.inflation[i]
            familyGift[i] = giftExps
        
        childExps = holiday.childBday + holiday.childXmas
        for i in range(self.years):
            childExps *= 1 + self.inflation[i]
            childGift[i] = childExps * self.isKids[i]
        
        holidayExps = (holiday.persBday + holiday.persXmas + holiday.persVal + holiday.persAnniv) * self.numInd
        for i in range(self.years):
            holidayExps *= 1 + self.inflation[i]
            total[i] += holidayExps + familyGift[i] + childGift[i]
        
        return total
    
    def edExp(self):
        education = self.vars.expenses.education
        
        total = np.zeros(self.years)
        
        edExps = education.tuition + education.housing + education.dining + education.books
        for i in range(self.years):
            edExps *= 1 + self.inflation[i]
            for j in range(len(self.childAges)):
                if self.childAges[j,i] >= 18 and self.childAges[j,i] < 22:
                    total[i] += edExps
        
        return total
    
    def vacExp(self):
        vacation = self.vars.expenses.vacation
        
        total = np.zeros(self.years)
        for i in range(self.years):   
            numDays = np.random.triangular(vacation.numDays[0],vacation.numDays[1],vacation.numDays[2])

            hotel   = np.random.triangular(vacation.hotel[0],vacation.hotel[1],vacation.hotel[2]) * numDays
            travel  = np.random.triangular(vacation.travel[0],vacation.travel[1],vacation.travel[2]) * self.numInd

            vacExp = hotel + travel + ((vacation.events + vacation.food + vacation.carRental) * numDays)
                 
            vacExp *= 1 + self.inflation[i]
            total[i] = vacExp * (1 + self.childInflation[i])
        
        return total
    
    def charExp(self):
        charity = self.vars.expenses.charity
        
        total = np.zeros(self.years)
        
        for i in range(self.iters):
            for j in range(self.years):
                total[j] += charity.baseChar * self.income[i,j]
        
        return total
    
    def majExp(self):
        major = self.vars.expenses.major
        
        total = np.zeros(self.years)
        
        for i in range(self.years):
            for _, event in major.majorSummary.iterrows():
                if event.purYr == i:
                    total[i] += event.cost
        
        return total
    
    def randExp(self):
        rand = self.vars.expenses.random
        
        total = np.zeros(self.years)
        
        expFunc = lambda x : np.exp(x * rand.decayFactor) - 1
        expDist = lambda r : expFunc(r) / expFunc(1)
        
        for i in range(self.years):
            total[i] = expDist(np.random.random()) * (rand.maxExp * self.summedInflation[i])
    
        return total