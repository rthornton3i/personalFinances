package com.personalfinances;

public class Setup {
    // Public Variables
    static int years;
    static int numInd;
    static int[] retAges;
    
    static int[] baseAges;
    static int[] childYrs;
    static int maxChildYr;
    
    static int[] salBases;
    static double[] salGrowth;
    static int[][] prevSal;
    static double wageInd;
    
    static String filingType;
    
    static Vars vars;
    static TaxDict taxes;
    
    // Private Variables
    private static int iters;
    private static int[] retYrs;
    
    private static int[][] salary;
    private static int[][] income;
    private static int[] grossIncome;
    
    private static int[][] ages;
    private static int[][] childAges;
    
    private static int[][] ssWages;
    private static int[][] primIns;
    
    public Setup(Vars vars, TaxDict taxes) {
        this.vars = vars;
        this.taxes = taxes;
        
        years = vars.base.years;
        numInd = vars.base.numInd;
        retAges = vars.base.retAges;
        
        baseAges = vars.base.baseAges;
        childYrs = vars.children.childYrs;
        maxChildYr = vars.children.maxChildYr;
        
        salBases = vars.salary.salBase;
        salGrowth = vars.salary.salGrowth;
        prevSal = vars.salary.prevSal;
        wageInd = vars.salary.wageInd;
        
        filingType = vars.filing.filingType;
    }
    
    public Vars run() {
        switch (filingType.toUpperCase()) {
            case "JOINT" -> iters = 1;
            case "SEPARATE", "SINGLE" -> iters = numInd;
        }
        
        retYrs = new int[numInd];
        for (int i = 0; i < numInd; i++) {
            retYrs[i] = retAges[i] - baseAges[i];
        }
                
        // Ages
        ages = new int[numInd][years];
        childAges = new int[childYrs.length][years];
        
        ageCalc();
        vars.base.ages = ages;
        vars.children.childAges = childAges;
        
        // Salary
        salary = new int[numInd][years];
        income = new int[iters][years];
        grossIncome = new int[years];
        
        salaryCalc();
        vars.salary.salary = salary;
        vars.salary.income = income;
        vars.salary.grossIncome = grossIncome;
                
        // Social Security
        ssWages = new int[iters][years+vars.salary.prevSal[0].length];
        primIns = new int[iters][years];
        
        socialSecurityCalc();
        vars.salary.ssIns = primIns;
        
        return vars;
    }
    
    static void salaryCalc() {
        for (int i = 0; i < numInd; i++) {
            salary[i][0] = salBases[i];
            
            for (int j = 1; j < years; j++) {
                if (j < retYrs[i]) {
                    salary[i][j] = (int) (salary[i][j-1] * (1 + Utility.Generator.triRand(salGrowth[0],salGrowth[1],salGrowth[2])));
                }
            }
        }
        
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                if (filingType.toUpperCase().equals("JOINT")) {
                    income[i][j] = Utility.ArrayMath.sumArray(new int[]{salary[0][j],salary[1][j]});
                } else if (filingType.toUpperCase().equals("SEPARATE")) {
                    income[i][j] = salary[i][j];
                } else if (filingType.toUpperCase().equals("SINGLE")) {
                    income[i][j] = salary[i][j];
                }
                
                grossIncome[j] += salary[i][j];
            }
        }
    }

    static void ageCalc() {
        for (int i = 0; i < years; i++) {
            for (int j = 0; j < numInd; j++) {
                ages[j][i] = baseAges[j] + i;
            }
                
            for (int j = 0; j < childYrs.length; j++) {
                if (i >= childYrs[j]) {
                    childAges[j][i] = i - childYrs[j];
                }
            }
        }
    }
    
    static void socialSecurityCalc() {
        TaxDict.Federal.Fica.Filing socialSecurity;
        
        switch (filingType.toUpperCase()) {
            case "JOINT" ->    socialSecurity = taxes.federal.fica.ss.joint;
            case "SEPARATE" -> socialSecurity = taxes.federal.fica.ss.separate;
            case "SINGLE" ->   socialSecurity = taxes.federal.fica.ss.single;
            default ->         socialSecurity = taxes.federal.fica.ss.single; // Assume Single 
        }
        
        for (int i = 0; i < iters; i++) {
            int prevYrs = prevSal[i].length;
            for (int j = 0; j < prevYrs; j++) {
                int yrInd = retYrs[i] - j;
                
                ssWages[i][j] = prevSal[i][j];
                ssWages[i][j] *= Math.exp(wageInd * yrInd);
                if (ssWages[i][j] > socialSecurity.maxSal) {
                    ssWages[i][j] = socialSecurity.maxSal;
                }
            }
            
            for (int j = 0; j < years; j++) {
                int yrInd = retYrs[i] - (j + prevYrs);
                
                ssWages[i][j+prevYrs] = salary[i][j];
                ssWages[i][j+prevYrs] *= Math.exp(wageInd * yrInd);
                if (ssWages[i][j+prevYrs] > socialSecurity.maxSal) {
                    ssWages[i][j+prevYrs] = socialSecurity.maxSal;
                }
            }
        }
    }
}
