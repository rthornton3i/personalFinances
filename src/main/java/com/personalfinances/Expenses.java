package com.personalfinances;

import java.lang.Math;

public class Expenses { //extends Thread {
    // Public Variables
    static int years;
    static int numInd;
    static int[][] income;
    
    static int[][] childAges;
    static int maxChildYr;
    
    static Vars vars;
    
    public Expenses(Vars vars) {
        this.vars = vars;
        
        years = vars.base.years;
        numInd = vars.base.numInd;
        income = vars.salary.income;
        
        childAges = vars.children.childAges;
        maxChildYr = vars.children.maxChildYr;
    }
    
    public Vars run() { //void run() {  
        Vars.Expenses exps = vars.expenses;
        Vars.Expenses.Housing.House house = vars.expenses.housing.house;
        Vars.Expenses.Cars cars = vars.expenses.cars;
        
        exps.housing.rent.totalRent = rentExp();
        exps.housing.house.totalHouse = housingExp();
        exps.cars.totalCar = carExp();
        
        exps.food.totalFood = foodExp();
        exps.entertain.totalEnt = entExp();
        exps.personalCare.totalPers = personalExp();
        exps.healthcare.totalHealth = healthExp();
        exps.pet.totalPet = petExp();
        
        exps.holiday.totalHol = holidayExp();
        exps.education.totalEd = edExp();
        exps.vacation.totalVac = vacExp();
        
        exps.charity.totalChar = charExp();
        exps.major.totalMajor = majExp();
        exps.random.totalRand = randExp();
        
        exps.totalExp =  Utility.ArrayMath.sumArrays(years, exps.housing.rent.totalRent, exps.housing.house.totalHouse, exps.cars.totalCar,
                                                            exps.food.totalFood, exps.entertain.totalEnt, exps.personalCare.totalPers, exps.healthcare.totalHealth, exps.pet.totalPet, exps.holiday.totalHol, exps.education.totalEd, exps.vacation.totalVac,
                                                            exps.charity.totalChar, exps.major.totalMajor, exps.random.totalRand,
                                                            house.houseDwn,cars.carDwn);
        
        exps.totalExpenses = new int[][]{Utility.ArrayMath.sumArrays(years,exps.housing.rent.totalRent, exps.housing.house.totalHouse, house.houseDwn),
                                         Utility.ArrayMath.sumArrays(years,exps.cars.totalCar,cars.carDwn),
                                         exps.food.totalFood, exps.entertain.totalEnt, exps.personalCare.totalPers, exps.healthcare.totalHealth, exps.pet.totalPet, exps.holiday.totalHol, exps.education.totalEd, exps.vacation.totalVac,
                                         exps.charity.totalChar, exps.major.totalMajor, exps.random.totalRand};
        
        return vars;
    }
    
    public int[] rentExp() {
        Vars.Expenses.Housing.Rent rent = vars.expenses.housing.rent;
        
        int[] totalRent = new int[years];
        
        for (int i = rent.rentYr[0]; i <= rent.rentYr[1]; i++) {
            totalRent[i] = (int) (rent.baseRent * Math.pow(1.0 + rent.rentInc, i)) * 12;
            totalRent[i] += (rent.repairs + rent.insurance + rent.electricity + rent.gas + rent.water) * 12;
        }
        
        return totalRent;
    }
    
    public int[] housingExp() {
        Vars.Expenses.Housing.House house = vars.expenses.housing.house;
        
        int[] totalHouse = new int[years];
        
        for (int i = house.purYr[0]; i < years; i++) {
            totalHouse[i] = house.housePay[i];
            totalHouse[i] += house.houseWth[i] * (house.repairs + house.insurance);
            totalHouse[i] += (house.electricity + house.gas + house.water) * 12;
        }
        
        return totalHouse;
    }
    
    public int[] carExp() {     
        Vars.Expenses.Cars cars = vars.expenses.cars;
        
        int[] totalCar = new int[years];
        
        for (int i = 0; i < years; i++) {
            totalCar[i] = cars.carPay[i];
//            System.out.println(cars.carWth[i] * (cars.repairs));
            for (int j = 0; j < childAges.length; j++) {
                if (childAges[j][i] > 16 && childAges[j][i] < maxChildYr) {
                    totalCar[i] += (cars.carWth[i] * (cars.repairs)) * (1 + cars.insRepChildFactor);
                    totalCar[i] += ((cars.insurance + cars.ezpass + cars.fuel) * 12) * (1 + cars.fuelEzChildFactor);
                } else {
                    totalCar[i] += cars.carWth[i] * (cars.repairs);
                    totalCar[i] += (cars.insurance + cars.ezpass + cars.fuel) * 12;
                }
            }
        }
        
        return totalCar;
    }
    
    public int[] foodExp() {        
        Vars.Expenses.Food food = vars.expenses.food;
        
        int[] totalFood = new int[years];
        
        for (int i = 0; i < years; i++) {
            totalFood[i] = (food.groceries + food.restaurants) * 12;
            totalFood[i] = (int) (totalFood[i] * (1 + ((double) i / years * food.growthFactor)));
            
            for (int j = 0; j < childAges.length; j++) {
                if (childAges[j][i] > 0 && childAges[j][i] < maxChildYr) {
                    totalFood[i] = (int) (totalFood[i] * (1 + food.childFactor));
                }
            }
        }
        
        return totalFood;
    }
    
    public int[] entExp() {
        Vars.Expenses.Entertain entertain = vars.expenses.entertain;
        
        int[] totalEnt = new int[years];
        
        for (int i = 0; i < years; i++) {
            totalEnt[i] = (entertain.wifi + entertain.cell + entertain.tv) * 12;
            totalEnt[i] = (int) (totalEnt[i] * (1 + ((double) i / years * entertain.growthFactor)));
            
            for (int j = 0; j < childAges.length; j++) {
                if (childAges[j][i] > 0 && childAges[j][i] < maxChildYr) {
                    totalEnt[i] = (int) (totalEnt[i] * (1 + entertain.childFactor));
                }
            }
        }
        
        return totalEnt;
    }
    
    public int[] personalExp() {
        Vars.Expenses.PersonalCare personalCare = vars.expenses.personalCare;
        
        int[] totalPers = new int[years];
        
        for (int i = 0; i < years; i++) {
            totalPers[i] = (personalCare.clothingShoes + personalCare.hairMakeup) * 12;
            totalPers[i] = (int) (totalPers[i] * (1 + ((double) i / years * personalCare.growthFactor)));
            
            for (int j = 0; j < childAges.length; j++) {
                if (childAges[j][i] > 0 && childAges[j][i] < maxChildYr) {
                    totalPers[i] = (int) (totalPers[i] * (1 + personalCare.childFactor));
                }
            }
        }
        
        return totalPers;
    }
    
    public int[] healthExp() {
        Vars.Expenses.Healthcare health = vars.expenses.healthcare;

        int[][] totalHealth = new int[numInd][years];
        int[][] totalHsa = new int[numInd][years];
        
        int[][] numVisits = {Utility.Generator.rangeRand(health.visits, years, "UNIFORM"),
                             Utility.Generator.rangeRand(health.visits, years, "UNIFORM")};
        
        int deductible;
        int maxOOP;
        for (int j = 0; j < years; j++) {
            for (int i = 0; i < numInd; i++) {
                deductible = health.deductible[i];
                maxOOP = health.maxOOP[i];
                for (int k = 0; k < numVisits[i][j]; k++) {
                    int cost = (int) (Utility.Generator.triRand(health.costs[0],health.costs[1],health.costs[2]));
                    
                    while (cost > 0) {
                        if (deductible > 0) {
                            if (cost > deductible) {
                                totalHealth[i][j] += deductible;
                                maxOOP -= deductible;
                                
                                cost -= deductible;
                                deductible = 0;
                            } else {
                                totalHealth[i][j] += cost;
                                maxOOP -= cost;
                                
                                deductible -= cost;
                                cost = 0;
                            }
                        } else if (maxOOP > 0) {
                            cost *= health.coinsurance[i];
                            if (cost > maxOOP) {
                                totalHealth[i][j] += maxOOP;
                                maxOOP = 0;
                            } else {
                                totalHealth[i][j] += cost;
                                maxOOP -= cost;
                            }
                            cost = 0;
                        } else {
                            cost = 0;
                        }
                    }
                }
                
                totalHealth[i][j] += health.drugs[i] * 12;
                
                for (int k = 0; k < childAges.length; k++) {
                    if (childAges[k][j] > 0 && childAges[k][j] < maxChildYr) {
                        totalHealth[i][j] = (int) (totalHealth[i][j] * (1 + health.childFactor));
                    }
                }
            }
        }
        
        return Utility.ArrayMath.sumArray2(totalHealth, 1);
    }        
    
    public int[] petExp() {
        Vars.Expenses.Pet pet = vars.expenses.pet;
        
        int[] totalPet = new int[years];
        
        for (int i = 0; i < years; i++) {
            totalPet[i] = (pet.food + pet.essentials + pet.toys + pet.careTaker + pet.vet + pet.insurance) * 12;
            totalPet[i] = (int) (totalPet[i] * (1 + ((double) i / years * pet.growthFactor)));
        }
        
        return totalPet;
    }
    
    public int[] holidayExp() {        
        Vars.Expenses.Holiday holiday = vars.expenses.holiday;
        
        int[] totalHol = new int[years];
           
        int[] familyGift = new int[years];
        for (int i = 0; i < years; i++) {
            familyGift[i] = holiday.familyBday + holiday.familyXmas; 
            familyGift[i] = (int) (familyGift[i] * (1 + ((double) i / years * holiday.familyGrowthFactor)));
        }
        
        int[] childGift = new int[years];
        for (int i = 0; i < years; i++) {
            for (int j = 0; j < childAges.length; j++) {
                if (childAges[j][i] > 0 && childAges[j][i] < maxChildYr) {
                    childGift[i] += holiday.childBday + holiday.childXmas;
                    childGift[i] = (int) (childGift[i] * (1 + ((double) i / years * holiday.childGrowthFactor)));
                }
            }
        }
        
        for (int i = 0; i < years; i++) {
            totalHol[i] += holiday.persBday * numInd +
                           holiday.persXmas * numInd + 
                           holiday.persVal * numInd + 
                           holiday.persAnniv * numInd + 
                           familyGift[i] + childGift[i];
        }
        
        return totalHol;
    }
    
    public int[] edExp() {
        Vars.Expenses.Education education = vars.expenses.education;
        
        int[] totalEd = new int[years];
        
        for (int i = 0; i < years; i++) {            
            for (int j = 0; j < childAges.length; j++) {
                if (childAges[j][i] >= 18 && childAges[j][i] < maxChildYr) {
                    totalEd[i] += education.tuition + education.housing + education.dining + education.books;
                }
            }
        }
        
        return totalEd;
    }
    
    public int[] vacExp() {
        Vars.Expenses.Vacation vacation = vars.expenses.vacation;
        
        int[] totalVac = new int[years];
        
        int numTravelers;
        for (int i = 0; i < years; i++) {
            numTravelers = numInd;
            for (int j = 0; j < childAges.length; j++) {
                if (childAges[j][i] >= 5 && childAges[j][i] < maxChildYr) {
                    numTravelers += 1;
                }
            }
            
            totalVac[i] += vacation.travel; // per person
            totalVac[i] += (vacation.events + vacation.food) * vacation.numDays; // per person per day            
            totalVac[i] *= numTravelers;
            
            totalVac[i] += (vacation.hotel + vacation.carRental) * vacation.numDays; // per day
            
            totalVac[i] = (int) (totalVac[i] * (1 + ((double) i / years * vacation.growthFactor)));
        }
        
        return totalVac;
    }
    
    public int[] charExp() {
        Vars.Expenses.Charity charity = vars.expenses.charity;
        
        int[] totalChar = new int[years];
        
        double charCont;
        for (int i = 0; i < income.length; i++) {
            for (int j = 0; j < years; j++) {
                charCont = charity.baseChar * (1 + ((double) j / years * charity.growthFactor));
                totalChar[j] += charCont * income[i][j];
            }
        }
        
        return totalChar;
    }
    
    public int[] majExp() {
        Vars.Expenses.Major major = vars.expenses.major;
        
        int[] totalMajor = new int[years];
        
        for (int i = 0; i < years; i++) {
            for (int[] wedEv : major.wedding) {
                if (wedEv[0] == i) {
                    totalMajor[i] += wedEv[1];
                }
            }
        }
        
        return totalMajor;
    }
    
    public int[] randExp() {
        Vars.Expenses.Random rand = vars.expenses.random;
        
        int[] totalRand = new int[years];
        
        // Reference
        double[] y = new double[years];
        for (int i = 0; i < years; i++) {
            y[i] = Math.exp((double) (-i / (double) (years / rand.decayFactor)));
        }
        
        double expWid = rand.maxExp * rand.binWid / years;
        
        int curBin;
        int expBin;
        double expense;
        
        for (int i = 0; i < years; i++) {
            curBin = (int) Math.floor(i / rand.binWid);
            
            while (true) {
                expense = -(rand.maxExp / rand.decayFactor) * Math.log(Math.random());
                expBin = (int) Math.floor(expense / expWid);
                
                if (expBin <= curBin) {
                    totalRand[i] = (int) expense;
                    break;
                }
            }
        }
    
        return totalRand;
    }
}