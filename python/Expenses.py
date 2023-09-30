import numpy as np
import matplotlib.pyplot as plt

class Expenses:
    def __init__(self, vars):
        self.vars = vars
        
        self.years = vars.base.years
        self.numInd = vars.base.numInd
        self.iters = vars.filing.iters
        
        self.income = vars.salary.income
        self.inflation = vars.salary.inflation
        
        self.childAges = vars.children.childAges
        self.maxChildYr = vars.children.maxChildYr
        self.childInflation = vars.children.childInflation
    
    def run(self):
        exp =  self.vars.expenses
        exp.rent.total = self.rentExp()
        exp.house.total = self.housingExp()
        exp.cars.total = self.carExp()
        
        exp.food.total = self.foodExp()
        exp.entertain.total = self.entExp()
        exp.personalCare.total = self.personalExp()
        exp.healthcare.total = self.healthExp()
        exp.pet.total = self.petExp()
        
        exp.holiday.total = self.holidayExp()
        exp.education.total = self.edExp()
        exp.vacation.total = self.vacExp()
        
        exp.charity.total = self.charExp()
        exp.major.total = self.majExp()
        exp.random.total = self.randExp()
        
        exp.totalExpenses = np.sum((exp.rent.total, \
                                    exp.house.total, \
                                    exp.cars.total, \
                                    exp.food.total, \
                                    exp.entertain.total, \
                                    exp.personalCare.total, \
                                    exp.healthcare.total, \
                                    exp.pet.total, \
                                    exp.holiday.total, \
                                    exp.education.total, \
                                    exp.vacation.total, \
                                    exp.charity.total, \
                                    exp.major.total, \
                                    exp.random.total),0)
        
        return self.vars
    
    def rentExp(self):
        rent = self.vars.expenses.rent
        
        total = np.zeros(self.years)
        
        if len(rent.rentYr) > 0:
            rentExp = (rent.baseRent + rent.rentFees) * 12
            rentExp += (rent.repairs + rent.insurance + rent.electricity + rent.gas + rent.water) * 12
            
            for i in range(rent.rentYr[0],rent.rentYr[1]+1):
                rentExp *= 1 + self.inflation[i]
                total[i] = rentExp
        
        return total
    
    def housingExp(self):
        house = self.vars.expenses.house
        
        total = np.zeros(self.years)
        
        firstYear = 0 if house.houseSummary.purYr[0] < 0 else house.houseSummary.purYr[0]

        homeUtil = (house.electricity + house.gas + house.water) * 12
        for i in range(firstYear,self.years):
            homeUtil *= 1 + self.inflation[i]

            total[i] = house.housePay[i]
            total[i] += np.random.triangular(house.repairs[0],house.repairs[1],house.repairs[2]) + house.insurance
            total[i] += homeUtil
        
        total += house.houseDwn

        return total
    
    def carExp(self):     
        cars = self.vars.expenses.cars
        
        total = np.zeros(self.years)
        
        carExps = (cars.insurance + cars.ezpass + cars.fuel) * 12 + np.random.triangular(cars.repairs[0],cars.repairs[1],cars.repairs[2]) * 12        
        for i in range(self.years):
            carExps *= 1 + self.inflation[i]
            total[i] = cars.carPay[i] + (carExps  * (1 + self.childInflation[i]))

        total += cars.carDwn

        return total
    
    def foodExp(self):        
        food = self.vars.expenses.food
        
        total = np.zeros(self.years)

        foodExps = (food.groceries + food.restaurants + food.alcohol + food.fastFood + food.workFood) * 12
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
            for j in range(len(self.childAges)):
                if self.childAges[j,i] > 0 and self.childAges[j,i] < self.maxChildYr:
                    childGift[i] = childExps
        
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
                if self.childAges[j,i] >= 18 and self.childAges[j,i] < self.maxChildYr:
                    total[i] = edExps
        
        return total
    
    def vacExp(self):
        vacation = self.vars.expenses.vacation
        
        total = np.zeros(self.years)
        
        numDays = np.random.triangular(vacation.numDays[0],vacation.numDays[1],vacation.numDays[2])
        vacExp = vacation.travel + ((vacation.events + vacation.food) * numDays) + ((vacation.hotel + vacation.carRental) * numDays)
        for i in range(self.years):            
            vacExp *= 1 + self.inflation[i]
            total[i] = vacExp * (1 + self.childInflation[i])
        
        return total
    
    def charExp(self):
        charity = self.vars.expenses.charity
        
        total = np.zeros(self.years)
        
        for i in range(self.iters):
            for j in range(self.years):
                total[j] += charity.baseChar * self.income[i][j]
        
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
        
        # Reference
        y = np.zeros(self.years)
        for i in range(self.years):
            y[i] = np.exp(-i / (self.years / rand.decayFactor))
        
        expWid = rand.maxExp * rand.binWid / self.years
        
        for i in range(self.years):
            curBin = np.floor(i / rand.binWid)
            
            while True:
                expense = -(rand.maxExp / rand.decayFactor) * np.log(np.random.random())
                expBin = np.floor(expense / expWid)
                
                if expBin <= curBin:
                    total[i] = expense
                    break
    
        return total