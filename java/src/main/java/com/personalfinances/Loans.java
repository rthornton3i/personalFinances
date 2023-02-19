package com.personalfinances;

import java.lang.Math;

public class Loans {
    static int years;
    
    static Vars.Expenses.Housing.House house;
    static Vars.Expenses.Cars car;
    
    static int[] loanBal;
    static int[] loanPay;
    static int[] loanPrn;
    static int[] loanInt;
    static int[] loanWth; 
    static int[] loanDwn;

    static int[] carPay;
    static int[] carWth;
    static int[] carDwn;
    
    static Vars vars;
    
    public Loans(Vars vars) {
        this.vars = vars;
        years = vars.base.years;
        
        house = vars.expenses.housing.house;
        car = vars.expenses.cars;
        
        loanBal  = new int[years];
        loanPay  = new int[years];
        loanPrn  = new int[years];
        loanInt  = new int[years];
        loanWth  = new int[years];
        loanDwn  = new int[years];
    }
    
    public Vars run() {     
        int preBal;
        int preWth;
        boolean sellPrev;
        
        // Housing Loans
        for (int i = 0; i < house.numHouses; i++) {
            if (i == 0) {
                preBal = house.preBal;
                preWth = house.preWth;
                sellPrev = false;
            } else {
                preBal = 0;
                preWth = 0;
                sellPrev = true;
            }
            
            loanCalc(   house.purYr[i],
                        house.sellYr[i],
                        house.term[i],
                        house.rate[i],
                        house.prin[i],
                        house.down[i],
                        house.app[i],
                        preBal,
                        preWth,
                        sellPrev);
        }
        
        house.houseBal  = loanBal;
        house.housePay  = loanPay;
        house.housePrn  = loanPrn;
        house.houseInt  = loanInt;
        house.houseWth  = loanWth;
        house.houseDwn  = loanDwn;
        
        // Reset Loan Variables
        loanBal  = new int[years];
        loanPay  = new int[years];
        loanPrn  = new int[years];
        loanInt  = new int[years];
        loanWth  = new int[years];
        loanDwn  = new int[years];
        
        // Car Loans
        for (int i = 0; i < car.numCars; i++) {
            if (i == 0) {
                preBal = car.preBal;
                preWth = car.preWth;
            } else {
                preBal = 0;
                preWth = 0;
            }
            
            loanCalc(   car.purYr[i],
                        car.sellYr[i],
                        car.term[i],
                        car.rate[i],
                        car.prin[i],
                        car.down[i],
                        car.app[i],
                        preBal,
                        preWth,
                        false);
        }
        
        car.carBal  = loanBal;
        car.carPay  = loanPay;
        car.carPrn  = loanPrn;
        car.carInt  = loanInt;
        car.carWth  = loanWth;
        car.carDwn  = loanDwn;
        
        return vars;
    }
    
    static void loanCalc(int purYr, int sellYr, int term, double rate, int prin, double down, double app, int preBal, int preWth, boolean sellPrev) {
        // Up to 1 house from previous year and 1 previous balance/worth        
        // Can only assume selling previous
        
        if (sellPrev) { 
            loanBal = curSet(loanBal,purYr);
            loanPay = curSet(loanPay,purYr);
            loanInt = curSet(loanInt,purYr);
            loanDwn = curSet(loanDwn,purYr);
            loanWth = curSet(loanWth,purYr); 
        }        

        rate /= 100 * 12;
        app /= 100 * 12;
        down /= 100;
        term *= 12;
        
        int downPay = (int) (down * prin);
        int prinPay;
        if (sellPrev) {
            prinPay = prin - loanWth[purYr-1] + loanBal[purYr-1];
        } else {
            prinPay = prin;
        }
        
        if (prinPay < downPay) {
            prinPay = 0;
        } else {
            prinPay -= downPay;
        }
        
        int[] monthBal  = new int[12];
        int[] monthPay  = new int[12];
        int[] monthPrin = new int[12];
        int[] monthInt  = new int[12];
        int[] monthWth  = new int[12];
        
        int arrSize;
        int yrInd;
        int end;
        
        if (purYr < 0) {
            arrSize = years + Math.abs(purYr);
            yrInd = 0;
        } else {
            arrSize = years;
            yrInd = purYr;
        }
        
        if (sellYr > purYr) {
            end = (sellYr - purYr) * 12;
        } else {
            end = years * 12;
        }
        
        int[] yearBal  = new int[arrSize];
        int[] yearPay  = new int[arrSize];
        int[] yearPrin = new int[arrSize];
        int[] yearInt  = new int[arrSize];
        int[] yearWth  = new int[arrSize];
        
        int mthInd = 0;
        for (int i = 0; i < end; i++) {
            double termConst = Math.pow((1 + rate),term);
            
            if (i < term) {
                monthBal[mthInd]  = (int) (prinPay * (termConst - Math.pow((1 + rate),i+1)) / (termConst - 1));
                monthPay[mthInd]  = (int) (prinPay * (rate * termConst) / (termConst - 1));
                if (monthBal[mthInd] < 0) {
                    monthPay[mthInd] += monthBal[mthInd];
                    monthBal[mthInd] = 0;
                }

                if (i % 12 > 0) {
                    monthPrin[mthInd] = monthBal[mthInd-1] - monthBal[mthInd];
                } else if (yrInd == purYr || yrInd == 0) {
                    monthPrin[mthInd] = prinPay - monthBal[mthInd];
                } else {
                    monthPrin[mthInd] = yearBal[yrInd-1] - monthBal[mthInd];
                }
                monthInt[mthInd]  = (int) (monthPay[mthInd] - monthPrin[mthInd]);
            } else {
                monthBal[mthInd]  = 0;
                monthPay[mthInd]  = 0;
                monthPrin[mthInd] = 0;
                monthInt[mthInd]  = 0;
            }
            
            monthWth[mthInd] = (int) (prin * Math.pow((1 + app),i));
            
            if (mthInd == 11) {
                if (i < term) {
                    yearBal[yrInd]  = monthBal[mthInd];
                    yearPay[yrInd]  = Utility.ArrayMath.sumArray(monthPay);
                    yearPrin[yrInd] = Utility.ArrayMath.sumArray(monthPrin);
                    yearInt[yrInd]  = Utility.ArrayMath.sumArray(monthInt);
                } else {
                    yearBal[yrInd]  = 0;
                    yearPay[yrInd]  = 0;
                    yearPrin[yrInd] = 0;
                    yearInt[yrInd]  = 0;
                }
                
                yearWth[yrInd]  = monthWth[mthInd];
                
                yrInd += 1;
                mthInd = 0;

                if (yrInd >= arrSize) {
                    break;
                }
            } else {
                mthInd += 1;
            }
        }
        
        if (purYr < 0) {
            yearBal  = arrTrim(yearBal,Math.abs(purYr),Math.abs(purYr)+years);
            yearPay  = arrTrim(yearPay,Math.abs(purYr),Math.abs(purYr)+years);
            yearPrin = arrTrim(yearPrin,Math.abs(purYr),Math.abs(purYr)+years);
            yearInt  = arrTrim(yearInt,Math.abs(purYr),Math.abs(purYr)+years);
            yearWth  = arrTrim(yearWth,Math.abs(purYr),Math.abs(purYr)+years);
        }
        
        loanBal  = Utility.ArrayMath.sumArrays(years,loanBal,yearBal);
        loanPay  = Utility.ArrayMath.sumArrays(years,loanPay,yearPay);
        loanPrn  = Utility.ArrayMath.sumArrays(years,loanPrn,yearPrin);
        loanInt  = Utility.ArrayMath.sumArrays(years,loanInt,yearInt);        
        loanWth  = Utility.ArrayMath.sumArrays(years,loanWth,yearWth);
        if (purYr >= 0) {
            loanDwn[purYr] += downPay;
        }  
    }
    
    private static int[] curSet(int[] vals, int purYr) {        
        int[] tempSet = new int[years];
        int[] curSet = arrRep(tempSet,arrTrim(vals, 0, purYr),0);

        return curSet;
    }

    private static int[] arrTrim(int[] arr, int start, int end) {
        /*
            Trims a larger array down to a smaller array between [start:end]
        */
        int[] arrInd = new int[end-start];

        int ind = 0;
        for (int i = start; i < end; i++) {
            arrInd[ind] = arr[i];
            ind += 1;
            
            if (i >= arr.length) {
                break;
            }
        }

        return arrInd;
    }    

    private static int[] arrRep(int[] origArr, int[] newArr, int start) {
        /*
            Replaces part of a larger array with values from a smaller array starting at [start]
        */
        int[] arrRep = origArr;
        
        int ind = start;
        for (int i = 0; i < newArr.length; i++) {
            arrRep[ind] = newArr[i];
            ind += 1;
            
            if (ind >= arrRep.length) {
                break;
            }
        }

        return arrRep;
    }
}