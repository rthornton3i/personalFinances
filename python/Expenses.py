import numpy as np
import math
import random

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
        exp.housing.rent.totalRent = self.rentExp()
        exp.housing.house.totalHouse = self.housingExp()
        exp.cars.totalCar = self.carExp()
        
        exp.food.totalFood = self.foodExp()
        exp.entertain.totalEnt = self.entExp()
        exp.personalCare.totalPers = self.personalExp()
        exp.healthcare.totalHealth = self.healthExp()
        exp.pet.totalPet = self.petExp()
        
        exp.holiday.totalHol = self.holidayExp()
        exp.education.totalEd = self.edExp()
        exp.vacation.totalVac = self.vacExp()
        
        exp.charity.totalChar = self.charExp()
        exp.major.totalMajor = self.majExp()
        exp.random.totalRand = self.randExp()
        
        exp.totalExpenses = np.sum((exp.housing.rent.totalRent, \
                                    exp.housing.house.totalHouse, \
                                    exp.cars.totalCar, \
                                    exp.food.totalFood, \
                                    exp.entertain.totalEnt, \
                                    exp.personalCare.totalPers, \
                                    exp.healthcare.totalHealth, \
                                    exp.pet.totalPet, \
                                    exp.holiday.totalHol, \
                                    exp.education.totalEd, \
                                    exp.vacation.totalVac, \
                                    exp.charity.totalChar, \
                                    exp.major.totalMajor, \
                                    exp.random.totalRand),0)
        
        return self.vars
    
    def rentExp(self):
        rent = self.vars.expenses.housing.rent
        
        totalRent = np.zeros(self.years)
        
        if len(rent.rentYr) > 0:
            rentExp = (rent.baseRent + rent.rentFees) * 12
            rentExp += (rent.repairs + rent.insurance + rent.electricity + rent.gas + rent.water) * 12
            
            for i in range(rent.rentYr[0],rent.rentYr[1]+1):
                rentExp *= 1 + self.inflation[i]
                totalRent[i] = rentExp
        
        return totalRent
    
    def housingExp(self):
        house = self.vars.expenses.housing.house
        
        totalHouse = np.zeros(self.years)
        
        firstYear = 0 if house.purYr[0] < 0 else house.purYr[0]
        
        for i in range(firstYear,self.years):
            totalHouse[i] = house.housePay[i]
            totalHouse[i] += house.houseWth[i] * (house.repairs + house.insurance)

        homeUtil = (house.electricity + house.gas + house.water) * 12
        for i in range(firstYear,self.years):
            homeUtil *= 1 + self.inflation[i]
            totalHouse[i] += homeUtil
        
        totalHouse += house.houseDwn

        return totalHouse
    
    def carExp(self):     
        cars = self.vars.expenses.cars
        
        totalCar = np.zeros(self.years)
        
        carExps = (cars.insurance + cars.ezpass + cars.fuel) * 12 + np.random.triangular(cars.repairs[0],cars.repairs[1],cars.repairs[2]) * 12        
        for i in range(self.years):
            carExps *= 1 + self.inflation[i]
            carExps *= 1 + self.childInflation[i]
            totalCar[i] = cars.carPay[i] + carExps

        totalCar += cars.carDwn

        return totalCar
    
    def foodExp(self):        
        food = self.vars.expenses.food
        
        totalFood = np.zeros(self.years)

        foodExps = (food.groceries + food.restaurants + food.alcohol + food.fastFood + food.workFood) * 12
        for i in range(self.years):
            foodExps *= 1 + self.inflation[i]
            foodExps *= 1 + self.childInflation[i]
            totalFood[i] = foodExps
            
        return totalFood
    
    def entExp(self):
        entertain = self.vars.expenses.entertain
        
        totalEnt = np.zeros(self.years)
        
        entertainExps = (entertain.wifi + entertain.cell + entertain.tv + entertain.subs) * 12
        for i in range(self.years):
            entertainExps *= 1 + self.inflation[i]
            entertainExps *= 1 + self.childInflation[i]
            totalEnt[i] = entertainExps

        return totalEnt
    
    def personalExp(self):
        personalCare = self.vars.expenses.personalCare
        
        totalPers = np.zeros(self.years)
        
        persExps = (personalCare.clothingShoes + personalCare.hairMakeup) * 12
        for i in range(self.years):
            persExps *= 1 + self.inflation[i]
            persExps *= 1 + self.childInflation[i]
            totalPers[i] = persExps
        
        return totalPers
    
    def healthExp(self):
        health = self.vars.expenses.healthcare

        numVisits = np.zeros((self.iters,self.years))

        totalHealth =np.zeros((self.iters,self.years))

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
                                totalHealth[i,j] += deductible
                                maxOOP -= deductible
                                
                                cost -= deductible
                                deductible = 0
                            else:
                                totalHealth[i,j] += cost
                                maxOOP -= cost
                                
                                deductible -= cost
                                cost = 0
                        elif maxOOP > 0:
                            cost *= health.coinsurance[i]
                            if cost > maxOOP:
                                totalHealth[i,j] += maxOOP
                                maxOOP = 0
                            else:
                                totalHealth[i,j] += cost
                                maxOOP -= cost

                            cost = 0
                        else:
                            cost = 0
                
                totalHealth[i,j] += health.drugs[i] * 12
                totalHealth[i,j] *= (1 + self.childInflation[i]) / self.iters
        
        return np.sum(totalHealth, 0)
    
    def petExp(self):
        pet = self.vars.expenses.pet
        
        totalPet = np.zeros(self.years)
        
        petExps = (pet.food + pet.essentials + pet.toys + pet.careTaker + pet.vet + pet.insurance) * 12
        for i in range(self.years):
            petExps *= 1 + self.inflation[i]
            totalPet[i] = petExps
        
        return totalPet
    
    def holidayExp(self):        
        holiday = self.vars.expenses.holiday

        familyGift = np.zeros(self.years)
        childGift = np.zeros(self.years)
        totalHol = np.zeros(self.years)
        
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
            totalHol[i] += holidayExps + familyGift[i] + childGift[i]
        
        return totalHol
    
    def edExp(self):
        education = self.vars.expenses.education
        
        totalEd = np.zeros(self.years)
        
        edExps = education.tuition + education.housing + education.dining + education.books
        for i in range(self.years):
            edExps *= 1 + self.inflation[i]
            for j in range(len(self.childAges)):
                if self.childAges[j,i] >= 18 and self.childAges[j,i] < self.maxChildYr:
                    totalEd[i] = edExps
        
        return totalEd
    
    def vacExp(self):
        vacation = self.vars.expenses.vacation
        
        totalVac = np.zeros(self.years)
        
        vacExp = (vacation.travel + ((vacation.events + vacation.food) * vacation.numDays) + ((vacation.hotel + vacation.carRental) * vacation.numDays)) * self.numInd
        for i in range(self.years):            
            vacExp *= 1 + self.inflation[i]
            vacExp *= 1 + self.childInflation[i]
            totalVac[i] = vacExp
        
        return totalVac
    
    def charExp(self):
        charity = self.vars.expenses.charity
        
        totalChar = np.zeros(self.years)
        
        for i in range(self.iters):
            for j in range(self.years):
                totalChar[j] += charity.baseChar * self.income[i][j]
        
        return totalChar
    
    def majExp(self):
        major = self.vars.expenses.major
        
        totalMajor = np.zeros(self.years)
        
        for i in range(self.years):
            for event in major.majEvent:
                if len(event) > 0:
                    if event[0] == i:
                        totalMajor[i] += event[1]
        
        return totalMajor
    
    def randExp(self):
        rand = self.vars.expenses.random
        
        totalRand = np.zeros(self.years)
        
        # Reference
        y = np.zeros(self.years)
        for i in range(self.years):
            y[i] = math.exp(-i / (self.years / rand.decayFactor))
        
        expWid = rand.maxExp * rand.binWid / self.years
        
        for i in range(self.years):
            curBin = math.floor(i / rand.binWid)
            
            while True:
                expense = -(rand.maxExp / rand.decayFactor) * math.log(random.random())
                expBin = math.floor(expense / expWid)
                
                if expBin <= curBin:
                    totalRand[i] = expense
                    break
    
        return totalRand