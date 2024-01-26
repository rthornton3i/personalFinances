from Vars import Vars

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Expenses:
    def __init__(self,vars:Vars):
        self.vars:Vars = vars
        
        self.years = vars.base.years
        self.numInd = vars.base.numInd
        self.iters = vars.filing.iters
        self.ages = vars.base.ages

        self.filingType = vars.filing.filingType.upper()
        
        self.income = vars.salary.income
        self.inflation = vars.salary.inflation
        self.summedInflation = vars.salary.summedInflation
        
        self.isKids = self.vars.children.isKids
        self.childAges = vars.children.childAges
        self.childInflation = vars.children.childInflation
    
    def run(self):
        exp = self.vars.expenses

        exp.totalExpenses = pd.DataFrame(0,index=np.arange(self.years),columns=exp.exps)

        exp.totalExpenses.house += self.rentExp()
        exp.totalExpenses.house += self.housingExp()
        exp.totalExpenses.cars = self.carExp()
        exp.totalExpenses.loans = self.loanExp()
        
        exp.totalExpenses.food = self.foodExp()
        exp.totalExpenses.shopping = self.shopExp()
        exp.totalExpenses.activities = self.activityExp()

        exp.totalExpenses.subscriptions = self.subsExp()
        exp.totalExpenses.personalCare = self.personalExp()
        exp.totalExpenses.healthcare = self.healthExp()
        exp.totalExpenses.pet = self.petExp()
        
        exp.totalExpenses.gifts = self.giftsExp()
        exp.totalExpenses.education = self.edExp()
        exp.totalExpenses.vacation = self.vacExp()
        
        exp.totalExpenses.major = self.majExp()
        exp.totalExpenses.random = self.randExp()

        self.vars.benefits.health.hsaDeposit = self.hsaDeposit

        # exps = [exp.rent,exp.house,exp.cars,exp.food,exp.subscriptions,exp.personalCare,exp.healthcare,exp.pet,exp.gifts,exp.education,exp.vacation,exp.charity,exp.major,exp.random]
        # legend = ['rent','house','cars','food','subscriptions','personalCare','healthcare','pet','gifts','education','vacation','charity','major','random']
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
                total[i] += np.random.triangular(rent.repairs[0],rent.repairs[1],rent.repairs[2]) * self.summedInflation[i]
        
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

        foodExps = (food.groceries + food.restaurants + food.other) * 12
        for i in range(self.years):
            foodExps *= 1 + self.inflation[i]
            total[i] = foodExps * (1 + self.childInflation[i])
            
        return total
    
    def shopExp(self):
        shop = self.vars.expenses.shopping
        
        total = np.zeros(self.years)

        shopExps = (shop.general + shop.other) * 12
        for i in range(self.years):
            shopExps *= 1 + self.inflation[i]
            total[i] = shopExps * (1 + self.childInflation[i])
            
        return total
        
    def activityExp(self):
        act = self.vars.expenses.activities
        
        total = np.zeros(self.years)

        actExps = (act.social + act.hobbies + act.sports + act.other) * 12
        for i in range(self.years):
            actExps *= 1 + self.inflation[i]
            total[i] = actExps * (1 + self.childInflation[i])
            
        return total

    def subsExp(self):
        subscriptions = self.vars.expenses.subscriptions
        
        total = np.zeros(self.years)
        
        subsExps = (subscriptions.internet + subscriptions.phone + np.nansum(subscriptions.tv) + np.nansum(subscriptions.software) + np.nansum(subscriptions.memberships)) * 12
        for i in range(self.years):
            subsExps *= 1 + self.inflation[i]
            total[i] = subsExps * (1 + self.childInflation[i])

        return total
    
    def personalExp(self):
        personalCare = self.vars.expenses.personalCare
        
        total = np.zeros(self.years)
        
        persExps = (personalCare.clothing + personalCare.shoes + personalCare.hair + personalCare.makeup + personalCare.other) * 12
        for i in range(self.years):
            persExps *= 1 + self.inflation[i]
            total[i] = persExps * (1 + self.childInflation[i])
        
        return total
    
    def healthExp(self):
        health = self.vars.expenses.healthcare
        healthBen = self.vars.benefits.health

        total = np.zeros((self.iters,self.years))
        self.hsaDeposit = np.zeros((self.iters,self.years))

        match self.filingType:
            case "JOINT": hsaLimit = healthBen.hsaLimit.joint
            case "SEPARATE", "SINGLE": hsaLimit = healthBen.hsaLimit.single        

        for j in range(self.years):
            for i in range(self.iters):
                if self.ages[i,j] >= 55:
                    hsaLimit += healthBen.hsaLimit.catchUp

                numVisits = np.round(np.random.triangular(health.visits[0],health.visits[1],health.visits[2])).astype(int)

                deductible = health.deductible[i] * self.summedInflation[j]
                maxOOP = health.maxOOP[i] * self.summedInflation[j]

                for _ in range(numVisits):
                    cost = np.random.triangular(health.costs[0],health.costs[1],health.costs[2]) * self.summedInflation[j]
                    
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
                
                total[i,j] += (health.drugs * 12) * self.summedInflation[j]
                total[i,j] *= (1 + self.childInflation[i]) / self.iters

                self.hsaDeposit[i,j] = min(total[i,j],hsaLimit)
        
        return np.sum(total, 0)
    
    def petExp(self):
        pet = self.vars.expenses.pet
        
        total = np.zeros(self.years)
        
        petExps = (pet.food + pet.essentials + pet.toys + pet.vet + pet.other) * 12
        for i in range(self.years):
            petExps *= 1 + self.inflation[i]
            total[i] = petExps
        
        return total
    
    def giftsExp(self):
        gifts = self.vars.expenses.gifts

        charity = np.zeros((self.iters,self.years))
        total = np.zeros(self.years)

        giftExps = np.sum(gifts.birthdays) + np.sum(gifts.holidays)
        for j in range(self.years):
            for i in range(self.iters):
                charity[i,j] = gifts.donations * self.income[i,j]
                total[j] += charity[i,j]
        
            giftExps *= 1 + self.inflation[j]
            total[j] += giftExps * (1 + self.childInflation[j])
        
        self.vars.expenses.charity = charity

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

            vacExp = (hotel + travel + ((vacation.events + vacation.food + vacation.carRental) * numDays)) * self.summedInflation[i]
            total[i] = vacExp * (1 + self.childInflation[i])
        
        return total
    
    def majExp(self):
        major = self.vars.expenses.major
        
        total = np.zeros(self.years)
        
        for i in range(self.years):
            for _, event in major.majorSummary.iterrows():
                expEvent = False
                if event.purYr == i:
                    expEvent = True
                elif event.isRepeat and i >= event.purYr:
                    expEvent = True

                if expEvent:
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