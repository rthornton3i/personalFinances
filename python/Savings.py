package com.personalfinances;

import java.lang.Math;

public class Savings {
    // Public Variables
    static int years;  
    static int numInd;
    
    static int[] netCash;
    static int numAccounts;
    static String[] accountName;
    
    static Vars vars;
    
    // Private Variables
    private static double[][] allocations;
    private static double[][] earnings;
    private static int[][] contributions;
    private static int[][] savings;
    private static int[][] withdrawals;
    
    public Savings(Vars vars) {
        this.vars = vars;
        
        years = vars.base.years;
        numInd = vars.base.numInd;
        
        netCash = vars.taxes.netCash;
        numAccounts = vars.allocations.numAccounts;
        accountName = vars.allocations.accountName;
    }
    
    public Vars run() {
        savings = new int[numAccounts][years];
        contributions = new int[numAccounts][years];
        withdrawals = new int[numAccounts][years];
        
        allocations = allocCalc(vars.allocations.allocations);
        earnings = earningCalc(vars.allocations.earnings,vars.allocations.accountType);
        
        savingsCalc();
        vars.savings.allocations = allocations;
        vars.savings.earnings = earnings;
        vars.savings.contributions = contributions;
        vars.savings.savings = savings;
        
        return vars;
    }
    
    public double[][] allocCalc(double[][] allocs) {
        double[][] allocations = new double[allocs.length][years];
        
        int binWid = (int) (years / (allocs[0].length - 1));
        
        for (int i = 0; i < numAccounts; i++) {
            for (int j = 0; j < years; j++) {
                if (j == 0) {
                    allocations[i][j] = allocs[i][0] / 100;
                } else {
                    int curBin = (int) (Math.floor(j / binWid));
                    allocations[i][j] = (allocs[i][curBin] + (((double) (j % binWid) / binWid) * (allocs[i][curBin+1] - allocs[i][curBin]))) / 100;
                }
            }
        }
        
        double[] totalAllocations = Utility.ArrayMath.sumArray2D(allocations, 1);
        for (int i = 0; i < numAccounts; i++) {
            for (int j = 0; j < years; j++) {
                allocations[i][j] /= totalAllocations[j];
            }
        }
        
        return allocations;
    }
    
    public double[][] earningCalc(double[][] earns, String[] accType) {
        double[][] earnings = new double[earns.length][years];
        
        for (int i = 0; i < numAccounts; i++) {
            for (int j = 0; j < years; j++) {
                if (earns[i].length == 2) {
                    earnings[i][j] = Utility.Generator.normalRand(earns[i][0],earns[i][1]);
                } else {
                    double[] mus    = {earns[i][0],earns[i][2]};
                    double[] sigmas = {earns[i][1],earns[i][3]};

                    double mu    = mus[0] - (((double) j / years) * (mus[0] - mus[1]));
                    double sigma = sigmas[0] - (((double) j / years) * (sigmas[0] - sigmas[1]));;

                    earnings[i][j] = Utility.Generator.normalRand(mu,sigma);
                }
                    
                if (accType[i].toUpperCase().equals("SAVINGS")) {
                    if (earnings[i][j] < 0) {
                        earnings[i][j] = 0;
                    }
                }
                
                earnings[i][j] /= 100;
            }
        }
        
        return earnings;
    }
    
    public void savingsCalc() {
        Vars.Benefits.Retirement ret = vars.benefits.retirement;
        Vars.Expenses exps = vars.expenses;
        Vars.Expenses.Housing.House house = vars.expenses.housing.house;
        Vars.Expenses.Cars cars = vars.expenses.cars;
        
        int[] expenses = new int[numAccounts];
                       
        for (int j = 0; j < years; j++) {
            // Retirement RMD
            double rmd = 0;
            int avgAge = 0;
            for (int i = 0; i < numInd; i++) {
                avgAge += vars.base.ages[i][j];
                if (j >= ret.rmdAge - vars.base.baseAges[i]) {
                    rmd += (double) vars.salary.salBase[i] / Utility.ArrayMath.sumArray(vars.salary.salBase);
                }
            }
            avgAge /= numInd;
            
            // EXPENSES
            for (int i = 0; i < numAccounts; i++) {
                switch (accountName[i].toUpperCase()) {
                    case "COLLEGE 529" -> {
                        expenses[i] = exps.education.totalEd[j];
                    }
                    case "LONG-TERM SAVINGS" -> {
                        expenses[i] = house.houseDwn[j] + cars.carDwn[j] + exps.major.totalMajor[j];  
                    }
                    case "SHORT-TERM SAVINGS" -> {
                        expenses[i] = exps.vacation.totalVac[j] + exps.charity.totalChar[j] + exps.random.totalRand[j];  
                    }
                    case "SPENDING" -> {
                        expenses[i] = exps.housing.rent.totalRent[j] + exps.housing.house.totalHouse[j] + exps.cars.totalCar[j] + 
                                      exps.food.totalFood[j] + exps.entertain.totalEnt[j] + exps.personalCare.totalPers[j] +
                                      exps.healthcare.totalHealth[j] + exps.pet.totalPet[j] + exps.holiday.totalHol[j];  
                    }
                }
            }
            
            // CONTRIBUTIONS
            int totalExpenses = Utility.ArrayMath.sumArray(expenses);
            int netCont;
            if (totalExpenses > netCash[j]) {
                netCont = netCash[j];
            } else {
                netCont = totalExpenses;
            }
            int remCash = netCash[j] - netCont;
            
            // SAVINGS
            for (int i = 0; i < numAccounts; i++) {                
                // CONTRIBUTIONS
                if (j == 0) {
                    savings[i][j] += vars.allocations.baseSavings[i];
                } else {
                    savings[i][j] += savings[i][j-1];
                }
                
                contributions[i][j] += (int) (((double) expenses[i] / totalExpenses) * netCont);
                contributions[i][j] += (int) (allocations[i][j] * remCash);
                savings[i][j] += contributions[i][j];
                
                // EXPENSES
                savings[i][j] -= expenses[i];
                int rmdDist = 0;
                switch (accountName[i].toUpperCase()) {
                    case "ROTH 401K", "TRADITIONAL 401K" -> {
                        if (rmd > 0) {
                            int accValue = (int) (savings[i][j] * rmd);
                            double ageFactor = avgAge * Math.pow(ret.rmdFactor[0],2) + avgAge * ret.rmdFactor[1] + ret.rmdFactor[2];
                            rmdDist = (int) (accValue / ageFactor);
                        }
                    }
                }
                
                switch (accountName[i].toUpperCase()) {
                    case "ROTH 401K" -> { // ROTH 401k
                        savings[i][j] += ret.netRothCont[j];
                        savings[i][j] -= rmdDist;
                    }
                    case "TRADITIONAL 401K" -> { // TRAD 401k                        
                        savings[i][j] += ret.netTradCont[j];
                        savings[i][j] -= rmdDist;
                    }
                }

                // EARNINGS
                if (savings[i][j] > 0) {
                    savings[i][j] *= 1 + earnings[i][j];
                }
            }
            
            // UNDERFLOW
            for (int[][] under : vars.allocations.underflow) {
                if (under.length == 3) {
                    if (j >= under[2][0]) {
                        Withdrawal withdrawal = underFlow(savings,j,under[0][0],under[1]);
                        savings = withdrawal.savings;
                    }
                } else {
                    Withdrawal withdrawal = underFlow(savings,j,under[0][0],under[1]);
                    savings = withdrawal.savings;
                }
            } 
            
            // OVERFLOW
            for (int[] over : vars.allocations.overflow) {
                if (over.length == 4) {
                    if (j >= over[3]) {
                        Withdrawal withdrawal = overFlow(savings,j,over[0],over[1],over[2]);
                        savings = withdrawal.savings;
                    }
                } else {
                    Withdrawal withdrawal = overFlow(savings,j,over[0],over[1],over[2]);
                    savings = withdrawal.savings;
                }
            }
            
            boolean childMax = false;
            for (int i = 0; i < vars.children.childAges.length; i++) {
                if (vars.children.childAges[i][j] > vars.children.maxChildYr) {
                    childMax = true;
                }
            }
            if (childMax) {
                Withdrawal withdrawal = overFlow(savings,j,7,8,0); // College to Long-Term (Excess)
                savings = withdrawal.savings;
            }
        }
    }
    
    private static Withdrawal overFlow(int[][] savingsIn, int yr, int indFrom, int indTo, int maxVal) {
        Withdrawal overFlow = new Withdrawal();
        
        int index = indFrom;
        int amount = 0;
        String capGains = vars.allocations.capGainsType[indFrom];
        int[][] savingsOut = savingsIn;
        
        if (savingsOut[indFrom][yr] > maxVal) {
            amount = savingsOut[indFrom][yr] - maxVal;
            savingsOut[indFrom][yr] = maxVal;
            savingsOut[indTo][yr] += amount;
        }
        
        overFlow.index = new int[]{index};
        overFlow.amount = new int[]{amount};
        overFlow.capGains = new String[]{capGains};
        overFlow.savings = savingsOut;
        
        return overFlow;
    }
    
    private static Withdrawal underFlow(int[][] savingsIn, int yr, int indTo, int[] indFrom) {
        Withdrawal underFlow = new Withdrawal();
        
        int[] index = new int[indFrom.length];
        int[] amount = new int[indFrom.length];
        String[] capGains = new String[indFrom.length];
        int[][] savingsOut = savingsIn;
        
        if (savingsOut[indTo][yr] < 0) {
            int transferVal = -savingsOut[indTo][yr];
            savingsOut[indTo][yr] = 0;
            
            int[] accVal = new int[indFrom.length];
            for (int i = 0; i < indFrom.length; i++) {
                accVal[i] = savingsOut[indFrom[i]][yr];
                if (accVal[i] < 0) {
                    accVal[i] = 0;
                }
            }
            int totalVal = Utility.ArrayMath.sumArray(accVal);
            
            for (int i = 0; i < indFrom.length; i++) {
                index[i] = indFrom[i];
                capGains[i] = vars.allocations.capGainsType[i];
                if (totalVal == 0) {
                    amount[i] = transferVal / indFrom.length;
                } else {
                    amount[i] = (int) (transferVal * ((double) accVal[i] / totalVal));
                }
                savingsOut[indFrom[i]][yr] -= amount[i];
            }
        }
        
        underFlow.index = index;
        underFlow.amount = amount;
        underFlow.capGains = capGains;
        underFlow.savings = savingsOut;
                
        return underFlow;
    }
    
    public static class Withdrawal {
        int[] index;
        int[] amount;
        String[] capGains;
        
        int[][] savings;
    }
}