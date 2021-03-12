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
    static double cola;
    static double[] bendPerc;
    static int[] bendPts;
    static double[][] bendSlope;
    
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
    
    private static int[][] ssIns;
    
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
        
        wageInd = vars.benefits.socialSecurity.wageInd;
        cola = vars.benefits.socialSecurity.cola;
        bendPts = vars.benefits.socialSecurity.bendPts;
        bendSlope = vars.benefits.socialSecurity.bendSlope;
        bendPerc = vars.benefits.socialSecurity.bendPerc;
        
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
        ssIns = new int[numInd][years];
        
        socialSecurityCalc();
        vars.benefits.socialSecurity.ssIns = ssIns;
        
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
        
        int[][] ssWages = new int[numInd][years+vars.salary.prevSal[0].length];
        int[] primIns = new int[iters];
        int[] aime = new int[numInd];
        
        switch (filingType.toUpperCase()) {
            case "JOINT" ->    socialSecurity = taxes.federal.fica.ss.joint;
            case "SEPARATE" -> socialSecurity = taxes.federal.fica.ss.separate;
            case "SINGLE" ->   socialSecurity = taxes.federal.fica.ss.single;
            default ->         socialSecurity = taxes.federal.fica.ss.single; // Assume Single 
        }
        
        int prevYrs;
        int yrInd;
        double growthFactor;
        for (int i = 0; i < iters; i++) {
            prevYrs = prevSal[i].length;
            for (int j = 0; j < prevYrs; j++) {
                yrInd = retYrs[i] - j;
                growthFactor = Math.exp(wageInd * yrInd);
                
                ssWages[i][j] = prevSal[i][j];
                ssWages[i][j] *= growthFactor;
                
                if (ssWages[i][j] > socialSecurity.maxSal * growthFactor) {
                    ssWages[i][j] = (int) (socialSecurity.maxSal * growthFactor);
                }
            }
            
            for (int j = 0; j < years; j++) {
                yrInd = retYrs[i] - (j + prevYrs);
                growthFactor = Math.exp(wageInd * yrInd);
                
                ssWages[i][j+prevYrs] = salary[i][j];
                ssWages[i][j+prevYrs] *= growthFactor;
                
                if (ssWages[i][j+prevYrs] > socialSecurity.maxSal * growthFactor) {
                    ssWages[i][j+prevYrs] = (int) (socialSecurity.maxSal * growthFactor);
                }
            }
            
            ssWages[i] = Utility.ArrayMath.maxArray(ssWages[i], 35);      
            aime[i] = Utility.ArrayMath.sumArray(ssWages[i]) / 35 / 12;
            
            int tempAime = aime[i];
            int prevBend = 0;
            for (int k = 0; k < 3; k++) {
                int bendPt;
                if (k < 2) {
                    bendPt = (int) (bendPts[k] + (retYrs[i] * (retYrs[i] * bendSlope[k][0] + bendSlope[k][1])));
                } else {
                    bendPt = (int) 1e9;
                }
                
                int bracketAmt;
                if (aime[i] > bendPt) {
                    bracketAmt = (int) (bendPerc[k] * (bendPt - prevBend));
                } else {
                    bracketAmt = (int) (bendPerc[k] * tempAime);
                }
                primIns[i] += bracketAmt;
                tempAime -= bracketAmt;
                
                prevBend = bendPt;
            }
            
            for (int j = retYrs[i], k = 1; j < years; j++, k++) {
                ssIns[i][j] = (int) (primIns[i] * Math.exp(cola * k) * 12);
            }
            
            // FULL RETIREMENT AGE ADJUSTMENTS
        }
    }
}
