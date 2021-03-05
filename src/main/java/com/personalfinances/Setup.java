package com.personalfinances;

import static com.personalfinances.Taxes.filingType;
import static com.personalfinances.Taxes.numInd;

public class Setup {
    // Public Variables
    static int years;
    static int numInd;
    static int[] retYrs;
    
    static int[] baseAges;
    static int[] childYrs;
    static int maxChildYr;
    
    static int[] salBases;
    static double[] salGrowth;
    
    static String filingType;
    
    static Vars vars;
    
    // Private Variables
    private static int iters;
    
    public Setup(Vars vars) {
        this.vars = vars;
        years = vars.base.years;
        numInd = vars.base.numInd;
        retYrs = vars.base.retYrs;
        
        baseAges = vars.base.baseAges;
        childYrs = vars.children.childYrs;
        maxChildYr = vars.children.maxChildYr;
        
        salBases = vars.salary.salBase;
        salGrowth = vars.salary.salGrowth;
        
        filingType = vars.filing.filingType;
    }
    
    public Vars run() {
        switch (filingType.toUpperCase()) {
            case "JOINT" -> iters = 1;
            case "SEPARATE", "SINGLE" -> iters = numInd;
        }
        
        ageCalc();
        salaryCalc();

        return vars;
    }
    
    static void salaryCalc() {
        vars.salary.salary = new int[numInd][years];
        vars.salary.income = new int[iters][years];
        vars.salary.grossIncome = new int[years];
        
        for (int i = 0; i < numInd; i++) {
            vars.salary.salary[i][0] = salBases[i];
            
            for (int j = 1; j < years; j++) {
                if (vars.base.ages[i][j] < retYrs[i]) {
                    vars.salary.salary[i][j] = (int) (vars.salary.salary[i][j-1] * (1 + Utility.Generator.triRand(salGrowth[0],salGrowth[1],salGrowth[2])));
                }
            }
        }
        
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                if (filingType.toUpperCase().equals("JOINT")) {
                    vars.salary.income[i][j] = Utility.ArrayMath.sumArray(new int[]{vars.salary.salary[0][j],vars.salary.salary[1][j]});
                } else if (filingType.toUpperCase().equals("SEPARATE")) {
                    vars.salary.income[i][j] = vars.salary.salary[i][j];
                } else if (filingType.toUpperCase().equals("SINGLE")) {
                    vars.salary.income[i][j] = vars.salary.salary[i][j];
                }
                
                vars.salary.grossIncome[j] += vars.salary.salary[i][j];
            }
        }
    }

    static void ageCalc() {
        vars.base.ages = new int[numInd][years];
        vars.children.childAges = new int[childYrs.length][years];
        vars.children.numChild = new int[years];
        
        for (int i = 0; i < years; i++) {
            for (int j = 0; j < numInd; j++) {
                vars.base.ages[j][i] = baseAges[j] + i;
            }
                
            for (int j = 0; j < childYrs.length; j++) {
                if (i >= childYrs[j]) {
                    vars.children.childAges[j][i] = i - childYrs[j];
                    
                    if (i <= childYrs[j] + maxChildYr) {
                        vars.children.numChild[i] += 1;
                    }
                }
            }
        }
    }
}
