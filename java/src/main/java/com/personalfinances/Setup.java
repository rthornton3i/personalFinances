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
    
    static String filingType;
    
    static Vars vars;
    static TaxDict taxes;
    
    // Private Variables
    private static int iters;
    
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
        
        filingType = vars.filing.filingType;
    }
    
    public Vars run() {
        switch (filingType.toUpperCase()) {
            case "JOINT" -> iters = 1;
            case "SEPARATE", "SINGLE" -> iters = numInd;
        }
        vars.filing.iters = iters;
                
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
    
    public static void salaryCalc() {        
        for (int i = 0; i < numInd; i++) {
            salary[i][0] = salBases[i];
            
            for (int j = 1; j < years; j++) {
                if (j < retAges[i] - baseAges[i]) {
                    salary[i][j] = (int) (salary[i][j-1] * (1 + Utility.Generator.triRand(salGrowth[0],salGrowth[1],salGrowth[2])));
                }
            }
        }
        
        switch (filingType.toUpperCase()) {
            case "JOINT" ->    income = new int[][] {Utility.ArrayMath.sumArray2(salary,1)};
            default ->         income = salary; // Assume Single
        }
    }

    public static void ageCalc() {
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
    
    public static void socialSecurityCalc() {
        TaxDict.Federal.Fica.Filing socialSecurity;
        Vars.Benefits.SocialSecurity ss = vars.benefits.socialSecurity;
        
        int[] colYrs = new int[numInd];
        for (int i = 0; i < numInd; i++) {
            colYrs[i] = ss.collectionAge[i] - baseAges[i];
        }
        
        int[][] ssWages = new int[numInd][years+prevSal[0].length];
        int[] primIns = new int[numInd];
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
        for (int i = 0; i < numInd; i++) {
            // SS WAGES
            prevYrs = prevSal[i].length;
            for (int j = 0; j < prevYrs; j++) {
                yrInd = colYrs[i] - j;
                growthFactor = Math.exp(ss.wageInd * yrInd);
                
                ssWages[i][j] = prevSal[i][j];
                ssWages[i][j] *= growthFactor;
                
                if (ssWages[i][j] > socialSecurity.maxSal) {
                    ssWages[i][j] = socialSecurity.maxSal;
                }
            }
            
            for (int j = 0; j < years; j++) {
                yrInd = colYrs[i] - (j + prevYrs);
                growthFactor = Math.exp(ss.wageInd * yrInd);
                
                ssWages[i][j+prevYrs] = salary[i][j];
                ssWages[i][j+prevYrs] *= growthFactor;
                
                if (ssWages[i][j+prevYrs] > socialSecurity.maxSal) {
                    ssWages[i][j+prevYrs] = socialSecurity.maxSal;
                }
            }
            
            ssWages[i] = Utility.ArrayMath.maxArray(ssWages[i], 35);      
            aime[i] = Utility.ArrayMath.sumArray(ssWages[i]) / 35 / 12;
            
            // BEND POINTS
            int tempAime = aime[i];
            int prevBend = 0;
            for (int k = 0; k < 3; k++) {
                int bendPt;
                if (k < 2) {
                    bendPt = ss.bendPts[k];
                } else {
                    bendPt = (int) 1e9;
                }
                
                int bracketAmt;
                if (aime[i] > bendPt) {
                    bracketAmt = (int) (ss.bendPerc[k] * (bendPt - prevBend));
                } else {
                    bracketAmt = (int) (ss.bendPerc[k] * tempAime);
                }
                primIns[i] += bracketAmt;
                tempAime -= bracketAmt;
                
                prevBend = bendPt;
            }
            
            // FULL RETIREMENT AGE ADJUSTMENTS
            int earlyClaim = 0;
            int lateClaim = 0;
            if (ss.collectionAge[i] < ss.fra) {
                earlyClaim = (ss.fra - ss.collectionAge[i]) * 12;
            } else {
                lateClaim = (ss.collectionAge[i] - ss.fra) * 12;
                if (lateClaim > 36) {
                    lateClaim = 36;
                }
            }
            
            if (earlyClaim > 36) {
                primIns[i] -= (int) (((36 * ss.fraEarly[0]) * primIns[i]) + (((earlyClaim - 36) * ss.fraEarly[1]) * primIns[i]));
            } else {
                primIns[i] -= (int) ((earlyClaim * ss.fraEarly[0]) * primIns[i]);
            }
            
            primIns[i] += (int) ((lateClaim * ss.fraLate) * primIns[i]);
            
            // COLA ADJUSTMENTS
            for (int j = colYrs[i], k = 1; j < years; j++, k++) {
                ssIns[i][j] = (int) (primIns[i] * Math.exp(ss.cola * k) * 12);
            }
        }
        
        switch (filingType.toUpperCase()) {
            case "JOINT" -> ssIns = new int[][]{Utility.ArrayMath.sumArray2(ssIns, 1)};
        }
    }
}
