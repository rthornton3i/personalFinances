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
        
        # exp.totalExp =  Utility.ArrayMath.sumArrays(self.years, exp.housing.rent.totalRent, exp.housing.house.totalHouse, exp.cars.totalCar,
        #                                                     exp.food.totalFood, exp.entertain.totalEnt, exp.personalCare.totalPers, exp.healthcare.totalHealth, exp.pet.totalPet, exp.holiday.totalHol, exp.education.totalEd, exp.vacation.totalVac,
        #                                                     exp.charity.totalChar, exp.major.totalMajor, exp.random.totalRand,
        #                                                     house.houseDwn,cars.carDwn)
        
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
            for i in range(rent.rentYr[0],rent.rentYr[1]+1):
                totalRent[i] = rent.baseRent * math.pow(1.0 + rent.rentInc, i) * 12
                totalRent[i] += (rent.repairs + rent.insurance + rent.electricity + rent.gas + rent.water) * 12
        
        return totalRent
    
    def housingExp(self):
        house = self.vars.expenses.housing.house
        
        totalHouse = np.zeros(self.years)
        
        firstYear = 0 if house.purYr[0] < 0 else house.purYr[0]
        
        for i in range(firstYear,self.years):
            totalHouse[i] = house.housePay[i]
            totalHouse[i] += house.houseWth[i] * (house.repairs + house.insurance)
            totalHouse[i] += (house.electricity + house.gas + house.water) * 12
        
        totalHouse += house.houseDwn

        return totalHouse
    
    def carExp(self):     
        cars = self.vars.expenses.cars
        
        totalCar = np.zeros(self.years)
        
        for i in range(self.years):
            totalCar[i] = cars.carPay[i]
            for j in range(len(self.childAges)):
                if self.childAges[j,i] > 16 and self.childAges[j,i] < self.maxChildYr:
                    totalCar[i] += (cars.carWth[i] * (cars.repairs)) * (1 + cars.insRepChildFactor)
                    totalCar[i] += ((cars.insurance + cars.ezpass + cars.fuel) * 12) * (1 + cars.fuelEzChildFactor)
                else:
                    totalCar[i] += cars.carWth[i] * (cars.repairs)
                    totalCar[i] += (cars.insurance + cars.ezpass + cars.fuel) * 12
        
        totalCar += cars.carDwn

        return totalCar
    
    def foodExp(self):        
        food = self.vars.expenses.food
        
        totalFood = np.zeros(self.years)
        
        for i in range(self.years):
            totalFood[i] = (food.groceries + food.restaurants + food.alcohol + food.fastFood + food.workFood) * 12
            totalFood[i] = totalFood[i] * (1 + (i / self.years * food.growthFactor))
            
            for j in range(len(self.childAges)):
                if self.childAges[j,i] > 0 and self.childAges[j,i] < self.maxChildYr:
                    totalFood[i] = totalFood[i] * (1 + food.childFactor)

        return totalFood
    
    def entExp(self):
        entertain = self.vars.expenses.entertain
        
        totalEnt = np.zeros(self.years)
        
        for i in range(self.years):
            totalEnt[i] = (entertain.wifi + entertain.cell + entertain.tv + entertain.subs) * 12
            totalEnt[i] = totalEnt[i] * (1 + (i / self.years * entertain.growthFactor))
            
            for j in range(len(self.childAges)):
                if self.childAges[j,i] > 0 and self.childAges[j,i] < self.maxChildYr:
                    totalEnt[i] = totalEnt[i] * (1 + entertain.childFactor)

        return totalEnt
    
    def personalExp(self):
        personalCare = self.vars.expenses.personalCare
        
        totalPers = np.zeros(self.years)
        
        for i in range(self.years):
            totalPers[i] = (personalCare.clothingShoes + personalCare.hairMakeup) * 12
            totalPers[i] = totalPers[i] * (1 + (i / self.years * personalCare.growthFactor))
            
            for j in range(len(self.childAges)):
                if self.childAges[j,i] > 0 and self.childAges[j,i] < self.maxChildYr:
                    totalPers[i] = totalPers[i] * (1 + personalCare.childFactor)
        
        return totalPers
    
    def healthExp(self):
        health = self.vars.expenses.healthcare

        numVisits = np.zeros((self.iters,self.years))

        totalHealth =np.zeros((self.iters,self.years))
        # totalHsa = new int[numInd,self.years]

        for j in range(self.years):
            for i in range(self.iters):
                numVisits = np.round(random.triangular(health.visits[0],health.visits[2],health.visits[1])).astype(int)

                deductible = health.deductible[i]
                maxOOP = health.maxOOP[i]
                for k in range(numVisits):
                    cost = random.triangular(health.costs[0],health.costs[2],health.costs[1])
                    
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
                
                for k in range(len(self.childAges)):
                    if self.childAges[k,j] > 0 and self.childAges[k,j] < self.maxChildYr:
                        totalHealth[i,j] = totalHealth[i,j] * (1 + health.childFactor)
        
        return np.sum(totalHealth, 0)
    
    def petExp(self):
        pet = self.vars.expenses.pet
        
        totalPet = np.zeros(self.years)
        
        for i in range(self.years):
            totalPet[i] = (pet.food + pet.essentials + pet.toys + pet.careTaker + pet.vet + pet.insurance) * 12
            totalPet[i] = totalPet[i] * (1 + (i / self.years * pet.growthFactor))
        
        return totalPet
    
    def holidayExp(self):        
        holiday = self.vars.expenses.holiday

        familyGift = np.zeros(self.years)
        
        totalHol = np.zeros(self.years)
           
        for i in range(self.years):
            familyGift[i] = holiday.familyBday + holiday.familyXmas 
            familyGift[i] = familyGift[i] * (1 + (i / self.years * holiday.familyGrowthFactor))
        
        childGift = np.zeros(self.years)
        for i in range(self.years):
            for j in range(len(self.childAges)):
                if self.childAges[j,i] > 0 and self.childAges[j,i] < self.maxChildYr:
                    childGift[i] += holiday.childBday + holiday.childXmas
                    childGift[i] = childGift[i] * (1 + (i / self.years * holiday.childGrowthFactor))
        
        for i in range(self.years):
            totalHol[i] += holiday.persBday * self.numInd + \
                           holiday.persXmas * self.numInd + \
                           holiday.persVal * self.numInd + \
                           holiday.persAnniv * self.numInd + \
                           familyGift[i] + childGift[i]
        
        return totalHol
    
    def edExp(self):
        education = self.vars.expenses.education
        
        totalEd = np.zeros(self.years)
        
        for i in range(self.years):            
            for j in range(len(self.childAges)):
                if self.childAges[j,i] >= 18 and self.childAges[j,i] < self.maxChildYr:
                    totalEd[i] += education.tuition + education.housing + education.dining + education.books
        
        return totalEd
    
    def vacExp(self):
        vacation = self.vars.expenses.vacation
        
        totalVac = np.zeros(self.years)
        
        for i in range(self.years):
            numTravelers = self.numInd
            for j in range(len(self.childAges)):
                if self.childAges[j,i] >= 5 and self.childAges[j,i] < self.maxChildYr:
                    numTravelers += 1
            
            totalVac[i] += vacation.travel # per person
            totalVac[i] += (vacation.events + vacation.food) * vacation.numDays # per person per day            
            totalVac[i] *= numTravelers
            
            totalVac[i] += (vacation.hotel + vacation.carRental) * vacation.numDays # per day
            
            totalVac[i] = totalVac[i] * (1 + (i / self.years * vacation.growthFactor))
        
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
            for wedEv in major.wedding:
                if wedEv[0] == i:
                    totalMajor[i] += wedEv[1]
        
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